from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
from .gif_loader import GifLoader

class Enemy(Widget):
    texture = ObjectProperty(None)
    velocity_x = NumericProperty(-3)

    def __init__(self, gif_path: str = 'assets/gifs/jacko.gif', size: tuple = (80, 80), **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.frames = GifLoader.load_gif_frames(gif_path)
        self.current_frame = 0
        self.frame_count = len(self.frames)
        self.textures = GifLoader.create_textures(self.frames)
        self.texture = self.textures[0]
        Clock.schedule_interval(self.update_frame, 0.1)

    def update_frame(self, dt: float) -> None:
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.texture = self.textures[self.current_frame]
        self.canvas.ask_update()

    def move(self) -> None:
        self.x += self.velocity_x