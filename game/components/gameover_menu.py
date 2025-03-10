from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class GameOverMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text="Game Over", font_size=40)
        restart_button = Button(text="Restart", size_hint=(1, 0.2))
        quit_button = Button(text="Quit", size_hint=(1, 0.2))
        
        restart_button.bind(on_press=self.restart_game)
        quit_button.bind(on_press=self.quit_game)
        
        layout.add_widget(title)
        layout.add_widget(restart_button)
        layout.add_widget(quit_button)
        
        self.add_widget(layout)
    
    def restart_game(self, instance):
        self.manager.current = 'game'
    
    def quit_game(self, instance):
        self.manager.current = 'start'