from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.core.window import Window
from .player import Character

class Enemy(Character):
    velocity_x = NumericProperty(-3)

    def __init__(self, gif_path: str = 'assets/gifs/jacko.gif', size: tuple = (80, 80), **kwargs):
        super().__init__(gif_path=gif_path, size=size, **kwargs)
        self.velocity_x = -3

    def move(self):
        self.velocity_y -= 0.10  # Gravity
        super().move()