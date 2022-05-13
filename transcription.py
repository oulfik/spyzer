from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty
from fileChooser import FileViewer, LoadDialog
from kivy.uix.popup import Popup
from kivy.app import App
import concurrent.futures
from kivy.clock import Clock
from functools import partial
from vosk import Model, KaldiRecognizer
from typing import List, Tuple, TypedDict
import os, json
import subprocess

Builder.load_file("layouts/transcription.kv")

class LoadFolderDialog(LoadDialog):
    filters = ListProperty([''])

class ModelChooser(FileViewer):
    path_label = StringProperty("Please select model folder")

    def show_load(self):
        content = LoadFolderDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select model folder", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        app = App.get_running_app()
        app.model_path = path
        self.path_label = f"Model folder: {path}"
        self.dismiss_popup()


class SpeechChooser(FileViewer):
    path_label = StringProperty("Please select folder with speech files")

    def show_load(self):
        content = LoadFolderDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select folder with speech files", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        app = App.get_running_app()
        app.speech_path = path
        self.path_label = f"Speech folder: {path}"
        self.dismiss_popup()

class ResultsChooser(FileViewer):
    path_label = StringProperty("Please select folder for the transcription results")

    def show_load(self):
        content = LoadFolderDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select folder for vosk results", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        app = App.get_running_app()
        app.transcription_res_path = path
        self.path_label = f"Transcription folder: {path}"
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
        print("Wait for vosk to analyze the audio file(s)...")
        
        for audio_file in os.listdir(app.speech_path):
            model = Model(app.model_path)
            rec = KaldiRecognizer(model, sample_rate)
            rec.SetWords(True)
            
            print(f"Analyzing audio file: {audio_file}")
            # converts audio file to appropriate format (ffmpeg needs to be installed)
            process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i',
                                        f"{app.speech_path}/{audio_file}",
                                        '-ar', str(sample_rate) , '-ac', '1', '-f', 's16le', '-'],
                                        stdout=subprocess.PIPE)

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
            return False


    def schedule_transcription(self):
        self.ids.start_btn.disabled = True
        self.ids.start_btn.text = "Please wait..."
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(self.vosk_output)
        Clock.schedule_interval(partial(self.future_is_running, future), 1)
     