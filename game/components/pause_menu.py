from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class PauseMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text="Paused", font_size=40)
        resume_button = Button(text="Resume", size_hint=(1, 0.2))
        quit_button = Button(text="Quit", size_hint=(1, 0.2))
        
        resume_button.bind(on_press=self.resume_game)
        quit_button.bind(on_press=self.quit_game)
        
        layout.add_widget(title)
        layout.add_widget(resume_button)
        layout.add_widget(quit_button)
        
        self.add_widget(layout)
    
    def resume_game(self, instance):
        self.manager.current = 'game'
    
    def quit_game(self, instance):
        self.manager.current = 'start'