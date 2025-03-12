from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from .gif_loader import GifLoader
from kivy.core.window import Window

class Enemy(Widget):
    texture = ObjectProperty(None)
    velocity_x = NumericProperty(-3)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

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
        self.velocity_y -= 0.10  # Apply gravity
        self.pos = Vector(*self.velocity) + self.pos
        # Boundary checking
        self.x = max(0, min(self.x, Window.width - self.width))
        if self.y <= 0:
            self.y = 0
            self.velocity_y = 0

    def on_pos(self, *args):
        # Check collision with platforms (called by Stage)
        pass