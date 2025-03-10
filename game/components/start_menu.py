from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class StartMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text="Dino Game", font_size=40)
        start_button = Button(text="Start", size_hint=(1, 0.2))
        settings_button = Button(text="Settings", size_hint=(1, 0.2))
        
        start_button.bind(on_press=self.start_game)
        settings_button.bind(on_press=self.go_to_settings)
        
        layout.add_widget(title)
        layout.add_widget(start_button)
        layout.add_widget(settings_button)
        
        self.add_widget(layout)
    
    def start_game(self, instance):
        self.manager.current = 'game'
    
    def go_to_settings(self, instance):
        self.manager.current = 'settings'