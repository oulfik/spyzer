from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.popup import Popup
import os
from kivy.lang import Builder
from utils import MyPopup

Builder.load_file('layouts/fileChooser.kv') 
Builder.load_file('layouts/myPopup.kv') 

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    filters = ListProperty(['*']) #specifies the filters to be applied to the files in the directory


class FileViewer(GridLayout):
    loadfile = ObjectProperty(None)
    path_label = StringProperty("Please select an audio file.")
    
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()


    def load(self, path, filename):
        file_path = os.path.join(path, filename[0])
        if ".wav" in file_path:
            self.path_label = file_path
            app = App.get_running_app()
            app.audio_file = self.path_label
        else:
            popup = MyPopup(title="Warning", text="You need to select an .wav audio file!")
            popup.open()

        self.dismiss_popup()






