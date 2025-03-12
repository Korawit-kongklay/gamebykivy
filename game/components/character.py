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
        self.frames = GifLoader.load_gif_frames(gif_path)
        self.current_frame = 0
        self.frame_count = len(self.frames)
        self.original_frames = GifLoader.create_textures(self.frames)
        self.flipped_frames = GifLoader.create_flipped_textures(self.frames)
        self.texture = self.original_frames[0]
        Clock.schedule_interval(self.update_frame, 0.1)

    def update_frame(self, dt: float) -> None:
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.texture = (self.original_frames if self.facing_right 
                       else self.flipped_frames)[self.current_frame]
        self.canvas.ask_update()

    def on_velocity_x(self, instance, value: float) -> None:
        self.facing_right = value >= 0

    def move(self) -> None:
        self.pos = Vector(*self.velocity) + self.pos
        # Boundary checking
        self.x = max(0, min(self.x, Window.width - self.width))
        self.y = max(0, self.y)
        if self.y == 0:
            self.velocity_y = 0