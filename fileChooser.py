from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
import os
from kivy.lang import Builder

Builder.load_file('layouts/fileChooser.kv') 



class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)



class FileViewer(FloatLayout):
    loadfile = ObjectProperty(None)
    text_label = StringProperty("Please select an audio file.")

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()


    def load(self, path, filename):
        print("FIELNAME" + os.path.join(path, filename[0]))
        self.text_label = os.path.join(path, filename[0])

        self.dismiss_popup()






