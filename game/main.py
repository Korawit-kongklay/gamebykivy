from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.properties import ListProperty, NumericProperty
from components.menubackground import GifLoader
from components.game import Game
from components.music_manager import MusicManager
import os

class MainMenu(BoxLayout):
    current_frame = NumericProperty(0)
    textures = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 20
        self.music_manager = MusicManager()
        self.menu_music_volume = 1.0
        self.effects_volume = 1.0
<<<<<<< HEAD
=======
        
        # โหลด background GIF
        self.load_background_gif()
>>>>>>> 83047c12ec58ca91e541a1c3d148d4ac34df08f8
        
        self.music_manager.play_menu_music()
        
        self.add_widget(Label(
            text='DinoCon',
            font_size=48,
            size_hint=(1, 0.4)
        ))
        
        self.start_button = Button(
            text='Start Game',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(0, 1, 0, 1)
        )
        self.start_button.bind(on_press=self.start_game)
        self.add_widget(self.start_button)
        
        self.settings_button = Button(
            text='Settings',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(0.5, 0.5, 1, 1)
        )
        self.settings_button.bind(on_press=self.show_settings)
        self.add_widget(self.settings_button)
        
        self.exit_button = Button(
            text='Exit',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(1, 0, 0, 1)
        )
        self.exit_button.bind(on_press=self.exit_game)
        self.add_widget(self.exit_button)

    def load_background_gif(self):
        try:
            # ปรับ path ให้ตรงกับโครงสร้างโฟลเดอร์: game/assets/gifs/darkforest.gif
            gif_path = os.path.join(os.path.dirname(__file__), 'assets', 'gifs', 'darkforest.gif')
            frames = GifLoader.load_gif_frames(gif_path)
            self.textures = GifLoader.create_textures(frames)
            if self.textures:
                # ใช้ขนาดของหน้าจอให้ GIF เต็มจอ
                self.size = Window.size
                with self.canvas.before:
                    Color(1, 1, 1, 1)
                    self.bg_rect = Rectangle(
                        pos=(0, 0),  # ตั้งค่าเริ่มต้นที่มุมล่างซ้าย
                        size=Window.size,  # ทำให้ขนาดเท่ากับหน้าจอ
                        texture=self.textures[0]
                    )
                # ผูกการอัพเดทขนาดหน้าจอ
                self.bind(size=self._update_rect, pos=self._update_rect)
                Clock.schedule_interval(self.update_background, 0.1)
            else:
                raise ValueError("No textures loaded for background")
        except Exception as e:
            print(f"Error loading background GIF: {e}")

    def _update_rect(self, instance, value):
        """อัพเดทตำแหน่งและขนาดของ Rectangle เมื่อหน้าจอเปลี่ยน"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

    def update_background(self, dt):
        if self.textures:
            self.current_frame = (self.current_frame + 1) % len(self.textures)
            self.bg_rect.texture = self.textures[self.current_frame]  # แก้ไขที่นี่

    def start_game(self, instance):
        self.music_manager.stop_music()
        app = App.get_running_app()
        app.root.clear_widgets()
<<<<<<< HEAD
        game = Game()
        game.music_manager.current_music.volume = self.menu_music_volume
        game.music_manager.set_effects_volume(self.effects_volume)
=======
        game = Game(music_manager=self.music_manager)
>>>>>>> 83047c12ec58ca91e541a1c3d148d4ac34df08f8
        app.root.add_widget(game)

    def show_settings(self, instance):
        settings_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        music_label = Label(text='Background Music Volume')
        settings_content.add_widget(music_label)
        
        music_slider = Slider(
            min=0,
            max=1,
            value=self.music_manager.music_volume,
            step=0.1
        )
        music_slider.bind(value=self.on_music_volume_change)
        settings_content.add_widget(music_slider)
        
        effects_label = Label(text='Sound Effects Volume')
        settings_content.add_widget(effects_label)
        
        effects_slider = Slider(
            min=0,
            max=1,
            value=self.music_manager.effects_volume,
            step=0.1
        )
        effects_slider.bind(value=self.on_effects_volume_change)
        settings_content.add_widget(effects_slider)
        
<<<<<<< HEAD
        # Add resize button for testing
        resize_button = Button(
            text='Resize Window (800x600)',
            size_hint=(1, 0.3)
        )
        resize_button.bind(on_press=self.resize_window)
        settings_content.add_widget(resize_button)
        
=======
>>>>>>> 83047c12ec58ca91e541a1c3d148d4ac34df08f8
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
<<<<<<< HEAD
        if self.music_manager.current_music:
            self.music_manager.current_music.volume = value
        self.menu_music_volume = value

    def on_effects_volume_change(self, instance, value):
        self.effects_volume = value
=======
        self.music_manager.set_music_volume(value)

    def on_effects_volume_change(self, instance, value):
>>>>>>> 83047c12ec58ca91e541a1c3d148d4ac34df08f8
        self.music_manager.set_effects_volume(value)

    def resize_window(self, instance):
        """Test resizing the window."""
        Window.size = (800, 600)  # Example size, adjust as needed

    def exit_game(self, instance):
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