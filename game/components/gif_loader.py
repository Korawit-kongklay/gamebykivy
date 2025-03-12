from typing import List
from kivy.graphics.texture import Texture
from PIL import Image
import os

class GifLoader:
    @staticmethod
    def load_gif_frames(gif_path: str) -> List[Image.Image]:
        if not os.path.exists(gif_path):
            raise FileNotFoundError(f"GIF file not found: {gif_path}")
        try:
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
        except Exception as e:
            raise ValueError(f"Failed to load GIF {gif_path}: {str(e)}")

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