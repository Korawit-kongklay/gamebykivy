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
from components.background import GifLoader
from components.game import Game
from components.music_manager import MusicManager
import os

class MainMenu(BoxLayout):
    current_frame = NumericProperty(0)
    textures = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 50
        self.spacing = 20  # คงระยะห่างระหว่างปุ่มไว้
        self.music_manager = MusicManager()
        self.music_manager.play_menu_music()

        # Load background GIF
        self.load_background_gif()

        # Menu title
        self.add_widget(Label(
            text='DinoCon',
            font_size=120,
            size_hint=(1, 0.3),  # ลดขนาด height ของ title เล็กน้อย
            bold=True
        ))

        # Start button
        self.start_button = Button(
            text='Start Game',
            size_hint=(0.4, 0.15),  # ปรับขนาดให้เล็กลงและสมส่วน
            pos_hint={'center_x': 0.5},
            background_color=(0, 1, 0, 1),
            font_size=24  # เพิ่มขนาดตัวอักษรให้ดูดีขึ้น
        )
        self.start_button.bind(on_press=self.start_game)
        self.add_widget(self.start_button)

        # Settings button
        self.settings_button = Button(
            text='Settings',
            size_hint=(0.4, 0.15),  # ขนาดเท่ากับ Start Button
            pos_hint={'center_x': 0.5},
            background_color=(0.5, 0.5, 1, 1),
            font_size=24
        )
        self.settings_button.bind(on_press=self.show_settings)
        self.add_widget(self.settings_button)

        # Exit button
        self.exit_button = Button(
            text='Exit',
            size_hint=(0.4, 0.15),  # ขนาดเท่ากันทั้งสามปุ่ม
            pos_hint={'center_x': 0.5},
            background_color=(1, 0, 0, 1),
            font_size=24
        )
        self.exit_button.bind(on_press=self.exit_game)
        self.add_widget(self.exit_button)

        # Bind window resize to update background
        Window.bind(on_resize=self.on_window_resize)

    def load_background_gif(self):
        """Load and animate the background GIF."""
        try:
            gif_path = os.path.join(os.path.dirname(__file__), 'assets', 'gifs', 'darkforest.gif')
            frames = GifLoader.load_gif_frames(gif_path)
            self.textures = GifLoader.create_textures(frames)
            if self.textures:
                self.size = Window.size
                with self.canvas.before:
                    Color(1, 1, 1, 1)
                    self.bg_rect = Rectangle(
                        pos=(0, 0),
                        size=Window.size,
                        texture=self.textures[0]
                    )
                self.bind(size=self._update_rect, pos=self._update_rect)
                Clock.schedule_interval(self.update_background, 0.1)
            else:
                raise ValueError("No textures loaded for background")
        except Exception as e:
            print(f"Error loading background GIF: {e}")
            # Fallback to solid color background
            with self.canvas.before:
                Color(0.2, 0.2, 0.2, 1)  # Dark gray fallback
                self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        """Update the position and size of the background rectangle."""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

    def update_background(self, dt):
        """Update the background GIF frame."""
        if self.textures:
            self.current_frame = (self.current_frame + 1) % len(self.textures)
            self.bg_rect.texture = self.textures[self.current_frame]

    def on_window_resize(self, window, width, height):
        """Handle window resize to update background size."""
        self.size = (width, height)
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size = (width, height)

    def start_game(self, instance):
        """Start the game by switching to the Game widget."""
        self.music_manager.stop_music()
        app = App.get_running_app()
        app.root.clear_widgets()
        game = Game(music_manager=self.music_manager)
        app.root.add_widget(game)

    def show_settings(self, instance):
        """Show the settings popup for volume control."""
        settings_content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Music volume control
        music_label = Label(text='Background Music Volume')
        settings_content.add_widget(music_label)
        music_slider = Slider(min=0, max=1, value=self.music_manager.music_volume, step=0.1)
        music_slider.bind(value=self.on_music_volume_change)
        settings_content.add_widget(music_slider)

        # Effects volume control
        effects_label = Label(text='Sound Effects Volume')
        settings_content.add_widget(effects_label)
        effects_slider = Slider(min=0, max=1, value=self.music_manager.effects_volume, step=0.1)
        effects_slider.bind(value=self.on_effects_volume_change)
        settings_content.add_widget(effects_slider)

        # Close button
        close_button = Button(text='Close', size_hint=(1, 0.3))
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
        """Update background music volume."""
        self.music_manager.set_music_volume(value)

    def on_effects_volume_change(self, instance, value):
        """Update sound effects volume."""
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