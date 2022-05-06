from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.properties import StringProperty

def window_hide_decorator(func):
    """ Hides the kivy main window until func returns"""
    def wrapper(*args, **kwargs):
        Window.hide()
        func(*args, **kwargs)
        Window.show()
    return wrapper


class MyPopup(Popup):
    title = StringProperty("") 
    text = StringProperty("") 


    "TODO: Exception handling"