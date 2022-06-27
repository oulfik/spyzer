from kivy.lang import Builder
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, StringProperty

import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np

from utils import window_hide_decorator, MyPopup

Builder.load_file("layouts/audio_analysis.kv")



class BaseDomain():
    frame_length = StringProperty("2048") #default frame length in librosa
    hop_length = StringProperty("512") #default hop length in librosa
    sound = ObjectProperty(None) #sound object for audio playback
    audio_feat_res = StringProperty("") #audio feature results specific for domain (frequency, time)


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
            popup = MyPopup(title="Error", text="Value must be a positive number!")
            popup.open()
        else:
            if self.ids.frame_length_input.text:
                self.frame_length = self.ids.frame_length_input.text
            if self.ids.hop_length_input.text:
                self.hop_length = self.ids.hop_length_input.text


class TimeDomain(GridLayout, BaseDomain):
    audio_feat_res = StringProperty("Computes time domain audio features. Zero crossing rate (ZCR) and root mean square of energy (RMSE).")
    audio_is_playing = False 
    
    def play_audio(self):
        file_path = self.get_current_file_path()
        if file_path and self.audio_is_playing == False:
            self.sound = SoundLoader.load(file_path)
            if self.sound:
                self.sound.play()
                self.audio_is_playing = True


    def stop_audio(self):
        if self.sound:
            self.sound.stop()
            self.audio_is_playing = False

    
    @window_hide_decorator
    def visualize_audio(self):
        file_path = self.get_current_file_path()
        if file_path:
            audio, _ = librosa.load(file_path, sr=None)

            plt.figure() 
            librosa.display.waveshow(audio, alpha=0.5) 
            plt.title("time signal")
            plt.show()


    @window_hide_decorator
    def visualize_audio_features(self):
        file_path = self.get_current_file_path()
        if file_path:
            zcr = self.compute_zcr(file_path)
            rms = self.compute_rms(file_path)
            frames = range(len(zcr))
            t = librosa.frames_to_time(frames, hop_length=int(self.hop_length))

            fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)
            ax[0].set(title='Zero crossing rate')
            ax[0].set(xlabel='time(s)')
            ax[0].set(ylabel='ZCR')
            ax[0].plot(t, zcr)
  
            ax[1].set(title='Root mean square')
            ax[1].set(xlabel='time(s)')
            ax[1].set(ylabel='RMS')
            ax[1].plot(t, rms)

            plt.show()
    


    def compute_zcr(self, file_path):
        audio, _ = librosa.load(file_path, sr=None)
        zcr_audio = librosa.feature.zero_crossing_rate(
            audio, 
            frame_length=int(self.frame_length), 
            hop_length=int(self.hop_length))[0]

        return zcr_audio
                
    
    def compute_rms(self, file_path):
        audio, _ = librosa.load(file_path, sr=None)
        rms_audio = librosa.feature.rms(
            audio, 
            frame_length=int(self.frame_length), 
            hop_length=int(self.hop_length))[0]

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
            audio, _ = librosa.load(file_path, sr=None)
            fig, ax = plt.subplots()
            S_audio = librosa.stft(audio, n_fft=int(self.frame_length), hop_length=int(self.hop_length))
            img = librosa.display.specshow(librosa.amplitude_to_db(S_audio,ref=np.max),
            y_axis='log', 
            x_axis='time', 
            ax=ax, hop_length=int(self.hop_length))
            ax.set_title('Power spectrogram')
            fig.colorbar(img, ax=ax, format="%+2.0f dB")
            plt.show()




    def compute_f0(self, file_path):
        audio, _ = librosa.load(file_path, sr=None)
        f0, _, _ = librosa.pyin(audio, 
        fmin=50, # expected minimum f0 frequency for a speech signal
        fmax=500, # expected maximum f0 frequency for a speech signal
        frame_length=int(self.frame_length), 
        hop_length=int(self.hop_length))
        return f0


    def compute_sc(self, file_path):
        audio, _ = librosa.load(file_path, sr=None)
        sc_audio = librosa.feature.spectral_centroid(
        y=audio, 
        n_fft=int(self.frame_length), 
        hop_length=int(self.hop_length))[0]
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
            audio, _ = librosa.load(file_path, sr=None)
            f0 = self.compute_f0(file_path)
            sc = self.compute_sc(file_path)
            times = librosa.times_like(f0, hop_length=int(self.hop_length))

            D = librosa.amplitude_to_db(np.abs(librosa.stft(audio, 
            hop_length=int(self.hop_length), 
            n_fft=int(self.frame_length))), 
            ref=np.max)
            fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True)
            img = librosa.display.specshow(D, 
                x_axis='time', 
                y_axis='log', 
                ax=ax[0], 
                hop_length=int(self.hop_length), 
                n_fft=int(self.frame_length))
            ax[0].set(title='pYIN fundamental frequency estimation')
            ax[0].plot(times, f0, label='f0', color='cyan', linewidth=3)
            ax[0].legend(loc='upper right')

            S, phase = librosa.magphase(librosa.stft(y=audio, hop_length=int(self.hop_length), 
            n_fft=int(self.frame_length)))
            librosa.display.specshow(librosa.amplitude_to_db(S, ref=np.max),
                                    y_axis='log', x_axis='time', ax=ax[1], 
                                    hop_length=int(self.hop_length), 
                                    n_fft=int(self.frame_length))
            ax[1].plot(times, sc.T, label='Spectral centroid', color='w')
            ax[1].legend(loc='upper right')
            fig.colorbar(img, ax=ax, format="%+2.f dB")
            ax[1].set(title='log Power spectrogram')
            plt.show()




