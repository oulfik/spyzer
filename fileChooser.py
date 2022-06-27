from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.uix.popup import Popup
import os
from kivy.lang import Builder
from utils import MyPopup

from os.path import sep, expanduser, isdir, dirname
from kivy_garden.filebrowser import FileBrowser
import sys

Builder.load_file('layouts/fileChooser.kv') 
Builder.load_file('layouts/myPopup.kv') 


class FileViewer(GridLayout):
    loadfile = ObjectProperty(None)
    attached_label = StringProperty("")
    popup_title = StringProperty("")
    supported_audio_files= ['mp3', 'wav', 'ogg', 'm4a']
    filter_files = ListProperty(['*'])
    allow_dir_selection = BooleanProperty(False)
    
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        if sys.platform == 'win':
            print("Here")
            user_path = dirname(expanduser('~')) + sep + 'Documents'
        else:
            user_path = expanduser('~') + sep + 'Documents'

        browser = FileBrowser(select_string='Select',
                              favorites=[(user_path, 'Documents')],
                              filters=self.filter_files,
                              dirselect=self.allow_dir_selection)
        browser.bind(
                    on_success=self._fbrowser_success,
                    on_canceled=self._fbrowser_canceled)
        self._popup = Popup(title=self.popup_title, content=browser,
                            size_hint=(0.9, 0.9))
        self._popup.open()


    def _fbrowser_canceled(self, instance):
        self.dismiss_popup()

    def _fbrowser_success(self, instance):
        audio_format = ""

        if instance.selection:
            file_path = instance.selection[0]
            audio_format = file_path.split('.')[-1]
        
        if audio_format in self.supported_audio_files:
            self.attached_label = file_path
            app = App.get_running_app()
            app.audio_file = file_path
        else:
            popup = MyPopup(title="Warning", text="Select an audio file with a supported format (mp3, wav, ogg, m4a)!")
            popup.open()

        self.dismiss_popup()









