#from pyAudioAnalysis import audioSegmentation as aS
import pyAudioAnalysis.audioSegmentation as aS
from pydub import AudioSegment
from typing import List, Tuple, TypedDict
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from fileChooser import FileViewer
from kivy.properties import NumericProperty
from utils import MyPopup, window_hide_decorator
from kivy.app import App
import concurrent.futures
from kivy.clock import Clock
from functools import partial


Builder.load_file("layouts/diarization.kv")


class SpeechFileChooser(FileViewer):
    def _fbrowser_success(self, instance):
        audio_format = ""

        if instance.selection:
            file_path = instance.selection[0]
            audio_format = file_path.split('.')[-1]
        
        if audio_format == 'wav':
            self.attached_label = file_path
            app = App.get_running_app()
            app.speech_file = file_path
        else:
            popup = MyPopup(title="Warning", text="You need to select a .wav audio file!")
            popup.open()

        self.dismiss_popup()
        

class DiarizationResultsChooser(FileViewer):
    def _fbrowser_success(self, instance):
        dir_path = instance.selection[0]
        app = App.get_running_app()
        app.diarization_res_path = dir_path
        self.attached_label = f"Segmentation folder: {dir_path}"
        self.dismiss_popup()


class Speaker(TypedDict):
    speaker_id: int #unique number for each speaker
    spoke_at: List[Tuple[float, float]] #start and end time in miliseconds



class Diarization(BoxLayout):
    num_of_speakers = NumericProperty()


    def segment_audio(self, speech_file):
        speaker_segments: List[Speaker] = []
        cls, _, _ = aS.speaker_diarization(speech_file, n_speakers=self.num_of_speakers, plot_res=False)

        start_time = 0
        for i in range(1, len(cls)):
            current_speaker_id = int(cls[i])
            previous_speaker_id = int(cls[i-1])
            if current_speaker_id != previous_speaker_id:

                if not speaker_segments:
                    speaker_segments.append(Speaker(speaker_id=previous_speaker_id, spoke_at=[(start_time * 100, (i-1) * 100)]))
                    start_time = i
                    continue

                found_spk_id = False
                for spk in speaker_segments:
                    if spk.get("speaker_id") == previous_speaker_id:
                        spk['spoke_at'].append((start_time * 100, (i-1) * 100))
                        start_time = i
                        found_spk_id = True
                
                if not found_spk_id:  
                    speaker_segments.append(Speaker(speaker_id=previous_speaker_id, spoke_at=[(start_time * 100, (i-1) * 100)]))
                    start_time = i

        #add last speaker segment not covered in the for-loop
        found_spk_id = False
        for spk in speaker_segments:
            if spk.get("speaker_id") == current_speaker_id:
                spk['spoke_at'].append((start_time * 100, (i) * 100))
                start_time = i
                found_spk_id = True
        
        if not found_spk_id:  
            speaker_segments.append(Speaker(speaker_id=current_speaker_id, spoke_at=[(start_time * 100, (i) * 100)]))
            start_time = i

        return speaker_segments


    def export_audio(self, speaker_segments: List[Speaker], audio_file, export_path):
        audio = AudioSegment.from_file(audio_file)
        for spk in speaker_segments:
            first_tuple = spk["spoke_at"].pop(0)
            audio_chunk = audio[first_tuple[0]:first_tuple[1]]
            for time_tuple in spk["spoke_at"]:
                audio_chunk = audio_chunk + audio[time_tuple[0]:time_tuple[1]]
            audio_chunk.export(f"{export_path}\Speaker{spk['speaker_id']}.wav", format="wav")

    
    @window_hide_decorator
    def speaker_plot(self):
        app = App.get_running_app()
        if app.speech_file and self.num_of_speakers:
            cls, _, _ = aS.speaker_diarization(app.speech_file, n_speakers=self.num_of_speakers, plot_res=True)


    def on_text_validate(self, widget):
        try:
            x = int(widget.text)
            if x < 2:
                raise ValueError
        except ValueError:
            popup = MyPopup(title="Error", text="Value must be a number greater than 2!")
            popup.open()
        else:
            self.num_of_speakers = x

    
    def future_is_running(self, future, dt):
        if not future.running():
            app = App.get_running_app()
            self.export_audio(future.result(), app.speech_file, app.diarization_res_path)
            self.ids.segment_btn.disabled = False
            self.ids.segment_btn.text = "Segment audio"
            popup = MyPopup(title="Info", text="Segmentation complete!")
            popup.open()
            return False


    def schedule_diarization(self):
        app = App.get_running_app()
        if app.speech_file and self.num_of_speakers and app.diarization_res_path:
            self.ids.segment_btn.disabled = True
            self.ids.segment_btn.text = "Please wait..."
            executor = concurrent.futures.ThreadPoolExecutor()
            future = executor.submit(self.segment_audio, app.speech_file)
            Clock.schedule_interval(partial(self.future_is_running, future), 1)
            