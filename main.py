from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand') #disable right click red dot on non-touch devices

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from navigation_screen_manager import NavigationScreenManager
from kivy.lang import Builder

Builder.load_file('layouts/spyzer.kv') 


class MyScreenManager(NavigationScreenManager):
    pass



class SpyzerApp(App):
    manager = ObjectProperty(None)

    # global variables for audio analysis functionality
    audio_file = StringProperty("")

    # global variables for transcription functionality
    model_path = StringProperty("")
    speech_path = StringProperty("")
    transcription_res_path = StringProperty("")

    #global variables for diarization functonality
    speech_file = StringProperty("")
    diarization_res_path = StringProperty("")

    def build(self):
        self.manager = MyScreenManager()
        return self.manager


SpyzerApp().run()


