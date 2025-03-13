from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from .gif_loader import GifLoader

class Character(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    texture = ObjectProperty(None)
    facing_right = BooleanProperty(True)

    def __init__(self, gif_path: str, size: tuple = (80, 80), **kwargs):
        super().__init__(**kwargs)
        self.size = size
        try:
            self.load_animations(gif_path)
            Clock.schedule_interval(self.update_frame, 0.1)
        except Exception as e:
            print(f"Failed to load animations from {gif_path}: {e}")

    def load_animations(self, gif_path: str):
        self.frames = GifLoader.load_gif_frames(gif_path)
        self.current_frame = 0
        self.frame_count = len(self.frames)
        self.original_frames = GifLoader.create_textures(self.frames)
        self.flipped_frames = GifLoader.create_flipped_textures(self.frames)
        self.texture = self.original_frames[0] if self.original_frames else None

    def update_frame(self, dt: float):
        if not self.frame_count or not self.original_frames:
            return
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.texture = self.original_frames[self.current_frame] if self.facing_right else self.flipped_frames[self.current_frame]
        self.canvas.ask_update()

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
        self.x = max(0, min(self.x, Window.width - self.width))

    def on_velocity_x(self, instance, value: float):
        self.facing_right = value >= 0

class Dino(Character):
    def __init__(self, **kwargs):
        super().__init__(gif_path='assets/gifs/ufopug.gif', **kwargs)