from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from fileChooser import FileViewer
from utils import MyPopup
from kivy.app import App
import concurrent.futures
from kivy.clock import Clock
from functools import partial
from vosk import Model, KaldiRecognizer
from typing import List, TypedDict
import os, json
import subprocess

Builder.load_file("layouts/transcription.kv")



class ModelChooser(FileViewer):
    def _fbrowser_success(self, instance):
        dir_path = instance.selection[0]
        app = App.get_running_app()
        app.model_path = dir_path
        self.attached_label = f"Model folder: {dir_path}"
        self.dismiss_popup()


class SpeechChooser(FileViewer):
    def _fbrowser_success(self, instance):
        dir_path = instance.selection[0]
        app = App.get_running_app()
        app.speech_path = dir_path
        self.attached_label = f"Speech folder: {dir_path}"
        self.dismiss_popup()


class ResultsChooser(FileViewer):
    def _fbrowser_success(self, instance):
        dir_path = instance.selection[0]
        app = App.get_running_app()
        app.transcription_res_path = dir_path
        self.attached_label = f"Transcription folder: {dir_path}"
        self.dismiss_popup()


class WordInfo(TypedDict):
    conf: float #confidence for specific word (from 0 to 1)
    end: float #end time for spoken word in sec
    start: float #start time of spoken word in sec
    word: str #detected word
        
class VoskResult(TypedDict):
    result: List[WordInfo] #list of statistics for each word
    text: str #spoken text


class Transcription(BoxLayout):
  
    
    def vosk_output(self):
        app = App.get_running_app()
        sample_rate=16000
        model = Model(app.model_path)
        rec = KaldiRecognizer(model, sample_rate)
        rec.SetWords(True)
        print("Wait for vosk to analyze the audio file(s)...")
        
        for audio_file in os.listdir(app.speech_path):
            print(f"Analyzing audio file: {audio_file}")
            # converts audio file to appropriate format (ffmpeg needs to be installed)
            process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                        f"{app.speech_path}/{audio_file}",
                                        '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                                        stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)

            json_array = []

            while True:
                data = process.stdout.read(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    if 'result' in res:
                        json_array.append(VoskResult(result=[WordInfo(**info) for info in res['result']] , text=res['text']))
                else:
                    pass

            final = json.loads(rec.FinalResult())
            if 'result' in final:
                json_array.append(VoskResult(result=[WordInfo(**info) for info in final['result']] , text=final['text']))

            with open(f'{app.transcription_res_path}/{audio_file[:-4]}_results.json', 'w') as json_res:
                json.dump(json_array, json_res)
                print("Created vosk results file!")
        print("Vosk finished audio file processing!")



    def future_is_running(self, future, dt):
        if not future.running():
            self.ids.start_btn.disabled = False
            self.ids.start_btn.text = "Start transcription"
            popup = MyPopup(title="Info", text="Transcription complete!")
            popup.open()
            return False


    def schedule_transcription(self):
        self.ids.start_btn.disabled = True
        self.ids.start_btn.text = "Please wait..."
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(self.vosk_output)
        Clock.schedule_interval(partial(self.future_is_running, future), 1)
     