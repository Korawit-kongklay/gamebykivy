from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class StartMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=50)
        layout.add_widget(Button(text='Start Game', on_press=self.start_game))
        layout.add_widget(Button(text='Settings', on_press=self.go_to_settings))
        layout.add_widget(Button(text='Exit', on_press=App.get_running_app().stop))
        self.add_widget(layout)
    
    def start_game(self, instance):
        self.manager.current = 'game'
    
    def go_to_settings(self, instance):
        self.manager.current = 'settings'