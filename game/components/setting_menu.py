from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider


class SettingsMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text="Settings", font_size=40)
        back_button = Button(text="Back", size_hint=(1, 0.2))
        
        volume_label = Label(text="Volume")
        volume_slider = Slider(min=0, max=100, value=50)
        
        difficulty_label = Label(text="Difficulty")
        difficulty_slider = Slider(min=1, max=3, value=1)
        
        back_button.bind(on_press=self.go_back)
        
        layout.add_widget(title)
        layout.add_widget(volume_label)
        layout.add_widget(volume_slider)
        layout.add_widget(difficulty_label)
        layout.add_widget(difficulty_slider)
        layout.add_widget(back_button)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'start'