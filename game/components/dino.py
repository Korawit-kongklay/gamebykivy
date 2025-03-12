from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from PIL import Image
import os

class Dino(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    texture = ObjectProperty(None)  # Texture property for the Rectangle

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load GIF frames
        self.frames = self.load_gif_frames('dinopug.gif')
        self.current_frame = 0
        self.frame_count = len(self.frames)
        self.texture = self.frames[self.current_frame]  # Set initial texture
        # Schedule frame updates
        Clock.schedule_interval(self.update_frame, 0.1)  # Adjust 0.1 for animation speed

    def load_gif_frames(self, gif_path):
        """Load all frames from the GIF and convert them to Kivy textures."""
        if not os.path.exists(gif_path):
            raise FileNotFoundError(f"GIF file not found: {gif_path}")
        
        gif = Image.open(gif_path)
        frames = []
        for frame in range(gif.n_frames):
            gif.seek(frame)
            # Convert frame to RGBA (Kivy needs this format)
            rgba_frame = gif.convert('RGBA').rotate(-180, expand=True)
            # Create a Kivy texture
            texture = Texture.create(size=(rgba_frame.width, rgba_frame.height), colorfmt='rgba')
            texture.blit_buffer(rgba_frame.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
            frames.append(texture)
        return frames

    def update_frame(self, dt):
        """Cycle through GIF frames."""
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.texture = self.frames[self.current_frame]
        self.canvas.ask_update()  # Force canvas to redraw with new texture

    def move(self):
        self.pos = Vector(0, self.velocity_y) + self.pos
        if self.y < 0:
            self.y = 0
            self.velocity_y = 0