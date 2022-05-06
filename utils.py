from kivy.core.window import Window

def window_hide_decorator(func):
    """ Hides the kivy main window until func returns"""
    def wrapper(*args, **kwargs):
        Window.hide()
        func(*args, **kwargs)
        Window.show()
    return wrapper


    "TODO: Exception handling"