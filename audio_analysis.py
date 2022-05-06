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
from kivy.uix.popup import Popup
from kivy.clock import Clock

import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np

from utils import window_hide_decorator

Builder.load_file("layouts/audio_analysis.kv")


class MyPopup(Popup):
    title = StringProperty("Error") 
    text = StringProperty("Value must be a positive number!") 

class StackLayoutExample(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.orientation = "lr-bt"
        for i in range(0, 100):
            #size = dp(100) + i*10
            size = dp(100)
            b = Button(text=str(i+1), size_hint=(None, None), size=(size, size))
            self.add_widget(b)

class BaseDomain():
    frame_length = StringProperty("") 
    hop_length = StringProperty("")
    sound = ObjectProperty(None)
    audio_feat_res = StringProperty("")
    plot_path = "images/analysis/"

    def get_current_file_path(self):
        app = App.get_running_app()
        file_path = app.audio_file 
        return file_path

    def on_text_validate(self, widget):
        try:
            x = int(widget.text)
            if x < 0:
                raise ValueError
        except ValueError:
            print("Value must be a positive Number!")
            popup = MyPopup()
            popup.open()
        else:
            if self.ids.frame_length_input.text:
                self.frame_length = self.ids.frame_length_input.text
            if self.ids.hop_length_input.text:
                self.hop_length = self.ids.hop_length_input.text


class TimeDomain(GridLayout, BaseDomain):
    audio_feat_res = StringProperty("Computes time domain audio features. Zero crossing rate (ZCR) and root mean square of energy (RMSE).")
    
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


    def visualize_audio_features(self):
        Window.hide()
        file_path = self.get_current_file_path()
        if file_path:
            zcr = self.compute_zcr(file_path)
            rms = self.compute_rms(file_path)
            frames = range(len(zcr))

            if self.hop_length:
                t = librosa.frames_to_time(frames, hop_length=int(self.hop_length))
            else:
                t = librosa.frames_to_time(frames)
        
            plt.figure()

            ax = plt.subplot(2, 1, 1)
            plt.plot(t, zcr)
            plt.xlabel("time(s)")
            plt.ylabel("ZCR")
            plt.title("Zero crossing rate")

            plt.subplot(2, 1, 2)
            plt.plot(t, rms)
            plt.xlabel("time(s)")
            plt.ylabel("RMS")
            plt.title("Root mean square")

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
        audio, _ = librosa.load(file_path)
        if self.frame_length and self.hop_length:
            rms_audio = librosa.feature.rms(
                audio, 
                frame_length=int(self.frame_length), 
                hop_length=int(self.hop_length))[0]
        else:
            rms_audio = librosa.feature.rms(
                audio)[0]
        return rms_audio       


    def get_audio_feat_res(self):
        file_path = self.get_current_file_path()
        if file_path:
            zcr = self.compute_zcr(file_path)
            rms = self.compute_rms(file_path)

            zcr_median = np.median(zcr)
            zcr_mean = np.mean(zcr)
            rms_median = np.median(rms)
            rms_mean = np.mean(rms)
        
        self.audio_feat_res = (f"Audio feature results:\n ZCR_mean: {zcr_mean}\n" 
                               f" ZCR_median: {zcr_median}\n RMS_mean: {rms_mean}\n RMS_median: {rms_median}")

            
        
 
class FrequencyDomain(GridLayout, BaseDomain):
    audio_feat_res = StringProperty("Computes frequency domain audio features. Fundamental frequency (F0) and spectral centroid (SC).")

    @window_hide_decorator
    def show_spectrogram(self):
        file_path = self.get_current_file_path()
        if file_path:
            audio, _ = librosa.load(file_path)
            fig, ax = plt.subplots()
            if self.frame_length and self.hop_length:
                S_audio = librosa.stft(audio, n_fft=int(self.frame_length), hop_length=int(self.hop_length))
                img = librosa.display.specshow(librosa.amplitude_to_db(S_audio,ref=np.max),
                y_axis='log', 
                x_axis='time', 
                ax=ax, hop_length=int(self.hop_length))
            else:
                S_audio = librosa.stft(audio)
                img = librosa.display.specshow(librosa.amplitude_to_db(S_audio,ref=np.max),
                y_axis='log',
                x_axis='time', 
                ax=ax)
            
            ax.set_title('Power spectrogram')
            fig.colorbar(img, ax=ax, format="%+2.0f dB")
            plt.show()




    def compute_f0(self, file_path):
        audio, _ = librosa.load(file_path)
        if self.frame_length and self.hop_length:
            f0, _, _ = librosa.pyin(audio, 
            fmin=50, # expected minimum f0 frequency for a speech signal
            fmax=500, # expected maximum f0 frequency for a speech signal
            frame_length=int(self.frame_length), 
            hop_length=int(self.hop_length))
        else:
            f0, _, _ = librosa.pyin(audio, 
            fmin=50, # expected minimum f0 frequency for a speech signal
            fmax=500) # expected maximum f0 frequency for a speech signal

        return f0


    def compute_sc(self, file_path):
        audio, _ = librosa.load(file_path)
        if self.frame_length and self.hop_length:
            sc_audio = librosa.feature.spectral_centroid(
            y=audio, 
            n_fft=int(self.frame_length), 
            hop_length=int(self.hop_length))[0]
        else:
            sc_audio = librosa.feature.spectral_centroid(y=audio)[0]
        
        return sc_audio
    

    def get_audio_feat_res(self):
        file_path = self.get_current_file_path()
        if file_path:
            f0 = self.compute_f0(file_path)
            f0_no_nans = f0[~np.isnan(f0)]
            sc = self.compute_sc(file_path)

            f0_median = np.median(f0_no_nans)
            f0_mean = np.mean(f0_no_nans)
            f0_range = np.max(f0_no_nans) - np.min(f0_no_nans)
            sc_median = np.median(sc)
            sc_mean = np.mean(sc)
        
        self.audio_feat_res = (
        f"Audio feature results:\n F0_mean: {f0_mean}\n" 
        f" F0_median: {f0_median}\n F0_range: {f0_range}\n SC_median: {sc_median}\n"
        f" SC_mean: {sc_mean}")


    @window_hide_decorator
    def visualize_audio_features(self):
        file_path = self.get_current_file_path()
        if file_path:
            audio, _ = librosa.load(file_path)
            f0 = self.compute_f0(file_path)
            sc = self.compute_sc(file_path)
            times = librosa.times_like(f0)

            if self.frame_length and self.hop_length:
                times = librosa.times_like(f0, hop_length=int(self.hop_length))
                D = librosa.amplitude_to_db(np.abs(librosa.stft(audio, 
                hop_length=int(self.hop_length), 
                n_fft=int(self.frame_length))), 
                ref=np.max)
                fig, ax = plt.subplots()
                img = librosa.display.specshow(D, 
                    x_axis='time', 
                    y_axis='log', 
                    ax=ax, 
                    hop_length=int(self.hop_length), 
                    n_fft=int(self.frame_length))
                ax.set(title='pYIN fundamental frequency estimation')
                fig.colorbar(img, ax=ax, format="%+2.f dB")
                ax.plot(times, f0, label='f0', color='cyan', linewidth=3)
                ax.legend(loc='upper right')

                fig, ax = plt.subplots()
                S, phase = librosa.magphase(librosa.stft(y=audio, hop_length=int(self.hop_length), 
                n_fft=int(self.frame_length)))
                librosa.display.specshow(librosa.amplitude_to_db(S, ref=np.max),
                                        y_axis='log', x_axis='time', ax=ax, 
                                        hop_length=int(self.hop_length), 
                                        n_fft=int(self.frame_length))
                ax.plot(times, sc.T, label='Spectral centroid', color='w')
                ax.legend(loc='upper right')
                fig.colorbar(img, ax=ax, format="%+2.f dB")
                ax.set(title='log Power spectrogram')
                plt.show()
            else:
                D = librosa.amplitude_to_db(np.abs(librosa.stft(audio)), ref=np.max)
                fig, ax = plt.subplots()
                img = librosa.display.specshow(D, x_axis='time', y_axis='log', ax=ax)
                ax.set(title='pYIN fundamental frequency estimation')
                fig.colorbar(img, ax=ax, format="%+2.f dB")
                ax.plot(times, f0, label='f0', color='cyan', linewidth=3)
                ax.legend(loc='upper right')

                fig, ax = plt.subplots()
                S, phase = librosa.magphase(librosa.stft(y=audio))
                librosa.display.specshow(librosa.amplitude_to_db(S, ref=np.max),
                                        y_axis='log', x_axis='time', ax=ax)
                ax.plot(times, sc.T, label='Spectral centroid', color='w')
                ax.legend(loc='upper right')
                fig.colorbar(img, ax=ax, format="%+2.f dB")
                ax.set(title='log Power spectrogram')
                plt.show()



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

