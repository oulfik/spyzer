from kivy.app import App
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from navigation_screen_manager import NavigationScreenManager
from kivy.lang import Builder

Builder.load_file('layouts/spyzer.kv') 

class MyScreenManager(NavigationScreenManager):
    pass



class SpyzerApp(App):
    manager = ObjectProperty(None)

    def build(self):
        self.manager = MyScreenManager()
        return self.manager


SpyzerApp().run()