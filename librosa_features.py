from kivy.lang import Builder
from kivy.metrics import dp
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.core.window import Window
from kivy.uix.popup import Popup

import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np

Builder.load_file("layouts/librosa_features.kv")


class MyPopup(Popup):
    title = "Error"
    text = "Value must be a positive number!"

class StackLayoutExample(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.orientation = "lr-bt"
        for i in range(0, 100):
            #size = dp(100) + i*10
            size = dp(100)
            b = Button(text=str(i+1), size_hint=(None, None), size=(size, size))
            self.add_widget(b)


class TimeDomain(GridLayout):
    frame_length = StringProperty("") 
    hop_length = StringProperty("")
    sound = ObjectProperty(None)
    audio_feat_res = StringProperty("Computes time domain audio features. Zero crossing rate (ZCR) and root mean square of energy (RMSE).")

    def get_current_file_path(self):
        app = App.get_running_app()
        file_path = app.audio_file 
        return file_path
    
    def play_audio(self):
        file_path = self.get_current_file_path()
        if file_path:
            self.sound = SoundLoader.load(file_path)
            if self.sound:
                print("Sound found at %s" % self.sound.source)
                print("Sound is %.3f seconds" % self.sound.length)
                self.sound.play()


    def stop_audio(self):
        if self.sound:
            self.sound.stop()

    

    def visualize_audio(self):
        Window.hide()
        file_path = self.get_current_file_path()
        if file_path:
            audio, _ = librosa.load(file_path)

            plt.figure() 
            librosa.display.waveshow(audio, alpha=0.5) 
            plt.title("time signal")
            plt.show()

        Window.show()

    def compute_zcr(self, file_path):
        audio, _ = librosa.load(file_path)
        if self.frame_length and self.hop_length:
            zcr_audio = librosa.feature.zero_crossing_rate(
                audio, 
                frame_length=int(self.frame_length), 
                hop_length=int(self.hop_length))[0]
        else:
            zcr_audio = librosa.feature.zero_crossing_rate(
                audio)[0]
        return zcr_audio
                
    
    def compute_rms(self, file_path):
        pass


    def compute_audio_feat_res(self):
        file_path = self.get_current_file_path()
        if file_path:
            zcr = self.compute_zcr(file_path)
            zcr_median = np.median(zcr)
            zcr_mean = np.mean(zcr)
        
        self.audio_feat_res = f"Audio feature results:\n ZCR_mean: {zcr_mean}\n ZCR_median: {zcr_median}"

            


    def on_text_validate(self, widget):
        try:
            x = int(widget.text)
        except ValueError:
            print("Value must be a positive Number!")
            popup = MyPopup()
            popup.open()
        else:
            if self.ids.frame_length_input.text:
                self.frame_length = self.ids.frame_length_input.text
            if self.ids.hop_length_input.text:
                self.hop_length = self.ids.hop_length_input.text
        
 



class AnchorLayoutExample(AnchorLayout):
    pass


class BoxLayoutExample(BoxLayout):

    """    def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.orientation = "vertical"
            b1 = Button(text="A")
            b2 = Button(text="B")
            b3 = Button(text="C")

            self.add_widget(b1)
            self.add_widget(b2)
            self.add_widget(b3)
    """

