from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.graphics import Ellipse, Color

class PowerUp(Widget):
    color = ObjectProperty(None)

    def __init__(self, color: tuple, **kwargs):
        super().__init__(**kwargs)
        self.size = (30, 30)
        with self.canvas:
            Color(rgba=color)
            self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.update_ellipse, size=self.update_ellipse)

    def update_ellipse(self, *args) -> None:
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size

class SpeedPowerUp(PowerUp):
    def __init__(self, **kwargs):
        super().__init__(color=(1, 1, 0, 1), **kwargs)  # Yellow

class ShieldPowerUp(PowerUp):
    def __init__(self, **kwargs):
        super().__init__(color=(0, 1, 1, 1), **kwargs)  # Cyan

class AmmoPowerUp(PowerUp):
    def __init__(self, **kwargs):
        super().__init__(color=(1, 0, 1, 1), **kwargs)  # Magenta

class HealthPowerUp(PowerUp):
    def __init__(self, **kwargs):
        super().__init__(color=(1, 0, 0, 1), **kwargs)  # Red

class ScorePowerUp(PowerUp):
    def __init__(self, **kwargs):
        super().__init__(color=(0, 1, 0, 1), **kwargs)  # Green