from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.graphics.svg import Svg

Builder.load_file("layouts/boxlayout_with_action_bar.kv")

class BoxLayoutWithActionBar(BoxLayout):
    title = StringProperty()