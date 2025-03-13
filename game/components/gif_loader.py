from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.properties import ListProperty, NumericProperty
from typing import List
from kivy.graphics.texture import Texture
from PIL import Image
import os

class GifLoader:
    @staticmethod
    def load_gif_frames(gif_path: str) -> List[Image.Image]:
        if not os.path.exists(gif_path):
            raise FileNotFoundError(f"GIF file not found: {gif_path}")
        with Image.open(gif_path) as gif:
            if not gif.is_animated:
                raise ValueError(f"File {gif_path} is not an animated GIF")
            frames = []
            for frame in range(gif.n_frames):
                gif.seek(frame)
                rgba_frame = gif.convert('RGBA').rotate(-180, expand=True)
                if rgba_frame.width <= 0 or rgba_frame.height <= 0:
                    raise ValueError(f"Invalid frame dimensions in {gif_path}: {rgba_frame.size}")
                frames.append(rgba_frame)
            return frames

    @staticmethod
    def create_textures(frames: List[Image.Image]) -> List[Texture]:
        textures = []
        for i, frame in enumerate(frames):
            texture = Texture.create(size=(frame.width, frame.height), colorfmt='rgba')
            if texture is None:
                raise RuntimeError(f"Failed to create texture for frame {i}: size={frame.size}")
            texture.blit_buffer(frame.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
            textures.append(texture)
        return textures

    @staticmethod
    def create_flipped_textures(frames: List[Image.Image]) -> List[Texture]:
        textures = GifLoader.create_textures(frames)
        for i, texture in enumerate(textures):
            if texture is None:
                raise RuntimeError(f"Texture {i} is None before flipping")
            texture.flip_horizontal()
        return textures

class Portal(Widget):
    current_frame = NumericProperty(0)
    textures = ListProperty([])

    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, 50)  # ปรับขนาดตาม GIF จริง
        self.pos = pos
        self.frame_duration = 0.1  # ความเร็วของแอนิเมชัน (วินาทีต่อเฟรม)
        self.load_gif()
        Clock.schedule_interval(self.update_animation, self.frame_duration)

    def load_gif(self):
        try:
            gif_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'gifs', 'portal.gif')
            frames = GifLoader.load_gif_frames(gif_path)
            self.textures = GifLoader.create_textures(frames)
            if self.textures:
                self.size = (self.textures[0].width, self.textures[0].height)  # ปรับขนาดตามเฟรมแรก
                with self.canvas:
                    Color(1, 1, 1, 1)  # สีพื้นฐาน (ขาวเต็มที่)
                    self.rect = Rectangle(pos=self.pos, size=self.size, texture=self.textures[0])
            else:
                raise ValueError("No textures loaded")
        except Exception as e:
            print(f"Error loading GIF: {e}")

    def update_animation(self, dt):
        if self.textures:
            self.current_frame = (self.current_frame + 1) % len(self.textures)
            self.rect.texture = self.textures[self.current_frame]

    def get_hitbox_rect(self):
        return {
            'x': self.x,
            'y': self.y,
            'right': self.x + self.width,
            'top': self.y + self.height
        }