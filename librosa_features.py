from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty

Builder.load_file("layouts/librosa_features.kv")


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
    sound = ObjectProperty(None)
    
    def play_audio(self):
        self.sound = SoundLoader.load('audio/test.wav')
        if self.sound:
            print("Sound found at %s" % self.sound.source)
            print("Sound is %.3f seconds" % self.sound.length)
            self.sound.play()


    def stop_audio(self):
        self.sound.stop()


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
