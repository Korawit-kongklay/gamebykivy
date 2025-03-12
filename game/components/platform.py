from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from PIL import Image
import os

class Platform(Widget):
    texture = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (37, 20)
        self.pos = (0, 0)
        with self.canvas:
            self.texture = self.load_texture('assets/images/grass.png')
            self.rect = Rectangle(pos=self.pos, size=self.size, texture=self.texture)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def load_texture(self, path: str) -> Texture:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        with Image.open(path) as image:
            texture = Texture.create(size=(image.width, image.height), colorfmt='rgba')
            texture.blit_buffer(image.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
            texture.wrap = 'repeat'
            return texture

    def update_rect(self, *args) -> None:
        self.rect.pos = self.pos
        self.rect.size = self.size