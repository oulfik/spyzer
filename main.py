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
    audio_file = StringProperty("")

    def build(self):
        self.manager = MyScreenManager()
        return self.manager


SpyzerApp().run()
