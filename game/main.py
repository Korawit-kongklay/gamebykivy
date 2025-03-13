# main_menu.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.core.window import Window
from components.game import Game
from components.music_manager import MusicManager

class MainMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 50
        self.spacing = 20
        self.music_manager = MusicManager()
        self.menu_music_volume = 1.0  # เก็บค่า volume สำหรับ background music
        self.effects_volume = 1.0     # เก็บค่า volume สำหรับ sound effects
        
        # เริ่มเล่นเพลงเมนู
        self.music_manager.play_menu_music()
        
        # Title
        self.add_widget(Label(
            text='Dino Game',
            font_size=48,
            size_hint=(1, 0.4)
        ))
        
        # Start Button
        self.start_button = Button(
            text='Start Game',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(0, 1, 0, 1)
        )
        self.start_button.bind(on_press=self.start_game)
        self.add_widget(self.start_button)
        
        # Settings Button
        self.settings_button = Button(
            text='Settings',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(0.5, 0.5, 1, 1)
        )
        self.settings_button.bind(on_press=self.show_settings)
        self.add_widget(self.settings_button)
        
        # Exit Button
        self.exit_button = Button(
            text='Exit',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(1, 0, 0, 1)
        )
        self.exit_button.bind(on_press=self.exit_game)
        self.add_widget(self.exit_button)

    def start_game(self, instance):
        """Switch to the game screen and pass music and effects volumes."""
        self.music_manager.stop_music()  # หยุดเพลงเมนู
        app = App.get_running_app()
        app.root.clear_widgets()
        game = Game()
        # ส่งต่อค่า volume ทั้ง background และ effects
        game.music_manager.current_music.volume = self.menu_music_volume
        game.music_manager.set_effects_volume(self.effects_volume)
        app.root.add_widget(game)

    def show_settings(self, instance):
        """Show settings popup with volume controls."""
        settings_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Background Music Volume Slider
        music_label = Label(text='Background Music Volume')
        settings_content.add_widget(music_label)
        
        music_slider = Slider(
            min=0,
            max=1,
            value=self.music_manager.current_music.volume if self.music_manager.current_music else 1.0,
            step=0.1
        )
        music_slider.bind(value=self.on_music_volume_change)
        settings_content.add_widget(music_slider)
        
        # Sound Effects Volume Slider
        effects_label = Label(text='Sound Effects Volume')
        settings_content.add_widget(effects_label)
        
        effects_slider = Slider(
            min=0,
            max=1,
            value=self.effects_volume,
            step=0.1
        )
        effects_slider.bind(value=self.on_effects_volume_change)
        settings_content.add_widget(effects_slider)
        
        # Close Button
        close_button = Button(
            text='Close',
            size_hint=(1, 0.3)
        )
        settings_content.add_widget(close_button)
        
        popup = Popup(
            title='Settings',
            content=settings_content,
            size_hint=(0.6, 0.6),
            auto_dismiss=True
        )
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def on_music_volume_change(self, instance, value):
        """Adjust background music volume and store it."""
        if self.music_manager.current_music:
            self.music_manager.current_music.volume = value
        self.menu_music_volume = value

    def on_effects_volume_change(self, instance, value):
        """Adjust sound effects volume and store it."""
        self.effects_volume = value
        self.music_manager.set_effects_volume(value)

    def exit_game(self, instance):
        """Exit the application."""
        self.music_manager.stop_music()
        App.get_running_app().stop()

class DinoApp(App):
    def build(self):
        Window.size = (1280, 720)
        return MainMenu()

if __name__ == '__main__':
    from kivy.config import Config
    Config.set('graphics', 'width', '1280')
    Config.set('graphics', 'height', '720')
    DinoApp().run()