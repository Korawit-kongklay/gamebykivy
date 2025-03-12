from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from PIL import Image
from kivy.core.window import Window
import os

class Dino(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    texture = ObjectProperty(None)
    facing_right = True  # Track the direction the Dino is facing

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frames = self.load_gif_frames('ufopug.gif')
        self.current_frame = 0
        self.frame_count = len(self.frames)
        # Store original frames (unflipped)
        self.original_frames = []
        for frame in self.frames:
            new_texture = Texture.create(size=(frame.width, frame.height), colorfmt='rgba')
            new_texture.blit_buffer(frame.pixels, colorfmt='rgba', bufferfmt='ubyte')
            self.original_frames.append(new_texture)
        # Store flipped versions of frames for left-facing
        self.flipped_frames = []
        for frame in self.original_frames:
            flipped_texture = Texture.create(size=(frame.width, frame.height), colorfmt='rgba')
            flipped_texture.blit_buffer(frame.pixels, colorfmt='rgba', bufferfmt='ubyte')
            flipped_texture.flip_horizontal()
            self.flipped_frames.append(flipped_texture)
        self.texture = self.original_frames[self.current_frame]  # Start facing right
        Clock.schedule_interval(self.update_frame, 0.1)

    def load_gif_frames(self, gif_path):
        if not os.path.exists(gif_path):
            raise FileNotFoundError(f"GIF file not found: {gif_path}")
        gif = Image.open(gif_path)
        frames = []
        for frame in range(gif.n_frames):
            gif.seek(frame)
            rgba_frame = gif.convert('RGBA').rotate(-180, expand=True)
            texture = Texture.create(size=(rgba_frame.width, rgba_frame.height), colorfmt='rgba')
            texture.blit_buffer(rgba_frame.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
            frames.append(texture)
        return frames

    def update_frame(self, dt):
        self.current_frame = (self.current_frame + 1) % self.frame_count
        # Use pre-flipped frames based on direction
        if self.facing_right:
            self.texture = self.original_frames[self.current_frame]
        else:
            self.texture = self.flipped_frames[self.current_frame]
        self.canvas.ask_update()

    def on_velocity_x(self, instance, value):
        """Update facing direction immediately when velocity_x changes."""
        if value < 0:  # Moving left
            self.facing_right = False
        elif value > 0:  # Moving right
            self.facing_right = True
        # If value == 0, retain last direction (no change)

    def move(self):
        self.pos = Vector(self.velocity_x, self.velocity_y) + self.pos
        if self.y < 0:
            self.y = 0
            self.velocity_y = 0
        if self.x < 0:
            self.x = 0
        elif self.x > Window.width - self.width:
            self.x = Window.width - self.width