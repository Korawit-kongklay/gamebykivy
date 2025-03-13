from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle, PushMatrix, PopMatrix, Rotate
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from PIL import Image
import os
from .hitbox import Hitbox  # Add this import

class Platform(Widget):
    texture = ObjectProperty(None)
    hitbox = ObjectProperty(None)  # Add hitbox property

    def __init__(self, pos: tuple, size: tuple = (31, 8), **kwargs):  
        super().__init__(**kwargs)
        self.pos = pos
        self.size = size
        # Initialize hitbox (matching the platform's full size)
        self.hitbox = Hitbox(
            offset_x=0,
            offset_y=0,
            width=size[0],
            height=size[1]
        )
        self.load_texture('assets/images/grass.png')
        self.update_graphics()

    def load_texture(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        with Image.open(path) as image:
            self.texture = Texture.create(size=(image.width, image.height), colorfmt='rgba')
            self.texture.blit_buffer(image.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
            self.texture.wrap = 'repeat'

    def update_graphics(self):
        with self.canvas:
            PushMatrix()
            self.rot = Rotate(angle=180, origin=(self.center_x, self.center_y))
            self.rect = Rectangle(pos=self.pos, size=self.size, texture=self.texture)
            PopMatrix()

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.rot.origin = (self.center_x, self.center_y)

    def get_hitbox_rect(self):
        return self.hitbox.get_rect(self.x, self.y)