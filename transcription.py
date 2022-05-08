from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ListProperty
from fileChooser import FileViewer, LoadDialog
from kivy.uix.popup import Popup
from kivy.app import App

from vosk import Model, KaldiRecognizer
from typing import List, Set, Any, Dict, Tuple, TypedDict, cast
import os, json
import subprocess

Builder.load_file("layouts/transcription.kv")

class LoadFolderDialog(LoadDialog):
    filters = ListProperty([''])

class ModelChooser(FileViewer):
    path_label = "Please select model folder"

    def show_load(self):
        content = LoadFolderDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select model folder", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        app = App.get_running_app()
        app.model_path = path
        self.dismiss_popup()


class SpeechChooser(FileViewer):
    path_label = "Please select folder with speech files"

    def show_load(self):
        content = LoadFolderDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select folder with speech files", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        app = App.get_running_app()
        app.speech_path = path
        self.dismiss_popup()

class ResultsChooser(FileViewer):
    path_label = "Please select folder for the transcription results"

    def show_load(self):
        content = LoadFolderDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Select folder for vosk results", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        app = App.get_running_app()
        app.transcription_res_path = path
        self.dismiss_popup()


class WordInfo(TypedDict):
    conf: float #confidence for specific word (from 0 to 1)
    end: float #end time for spoken word in sec
    start: float #start time of spoken word in sec
    word: str #detected word
        
class VoskResult(TypedDict):
    result: List[WordInfo] #list of statistics for each word
    text: str #spoken text

class WordCount(TypedDict):
    word: str #word to be counted
    count: int #count of spoken word

class WordOccurrence(TypedDict):
    word: str #word that occurred in speech
    occurrences: List[Tuple[float, float]] #start and end time in sec for spoken word



class Transcription(BoxLayout):
    test = StringProperty("")
    
    def vosk_output(self) -> None:
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
                    #print(res)
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