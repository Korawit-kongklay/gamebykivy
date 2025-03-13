from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle, PushMatrix, PopMatrix, Rotate, Line, Color
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from PIL import Image
import os
from .hitbox import Hitbox

class Platform(Widget):
    texture = ObjectProperty(None)
    hitbox = ObjectProperty(None)

    def __init__(self, pos: tuple, size: tuple = (93, 24), **kwargs):
        super().__init__(**kwargs)
        self.pos = pos
        self.size = size
        self.hitbox = Hitbox(offset_x=0, offset_y=0, width=self.size[0], height=self.size[1])
        self.debug_hitbox_visible = False
        self.debug_hitbox_instruction = None
        self.load_texture('assets/images/grass.png')
        self.update_graphics()
        # Bind to size changes to update hitbox
        self.bind(size=self.update_hitbox_size)

    def load_texture(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        with Image.open(path) as image:
            self.texture = Texture.create(size=(self.size[0], self.size[1]), colorfmt='rgba')
            # Resize image to match dynamic platform size
            resized_image = image.resize((int(self.size[0]), int(self.size[1])), Image.Resampling.LANCZOS)
            self.texture.blit_buffer(resized_image.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
            self.texture.wrap = 'repeat'

    def update_graphics(self):
        self.canvas.clear()
        with self.canvas:
            PushMatrix()
            self.rot = Rotate(angle=180, origin=(self.center_x, self.center_y))
            self.rect = Rectangle(pos=self.pos, size=self.size, texture=self.texture)
            PopMatrix()
        self.bind(pos=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.rot.origin = (self.center_x, self.center_y)
        self.update_hitbox_debug()

    def update_hitbox_size(self, instance, value):
        """Update hitbox size when platform size changes."""
        self.hitbox.width = self.size[0]
        self.hitbox.height = self.size[1]
        self.load_texture('assets/images/grass.png')  # Reload texture with new size
        self.update_graphics()
        self.update_hitbox_debug()

    def get_hitbox_rect(self):
        return self.hitbox.get_rect(self.x, self.y)

    def toggle_hitbox_debug(self, visible: bool):
        """Show or hide the hitbox debug outline."""
        self.debug_hitbox_visible = visible
        if visible:
            self.update_hitbox_debug()
        else:
            if self.debug_hitbox_instruction:
                self.canvas.after.remove(self.debug_hitbox_instruction)
                self.debug_hitbox_instruction = None

    def update_hitbox_debug(self):
        """Update the hitbox debug outline position and size."""
        if not self.debug_hitbox_visible:
            return
        hitbox_rect = self.get_hitbox_rect()
        if self.debug_hitbox_instruction:
            self.canvas.after.remove(self.debug_hitbox_instruction)
        with self.canvas.after:
            Color(0, 1, 0, 1)  # Green outline for platforms
            self.debug_hitbox_instruction = Line(
                rectangle=(
                    hitbox_rect['x'], hitbox_rect['y'],
                    hitbox_rect['width'], hitbox_rect['height']
                ),
                width=1
            )