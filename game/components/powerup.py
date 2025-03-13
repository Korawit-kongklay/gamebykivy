from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

class PowerUp(Widget):
    def __init__(self, pos: tuple, **kwargs):
        super().__init__(**kwargs)
        self.size = (30, 30)
        self.pos = pos

class SpeedPowerUp(PowerUp): pass
class ShieldPowerUp(PowerUp): pass
class AmmoPowerUp(PowerUp): pass
class HealthPowerUp(PowerUp): pass
class ScorePowerUp(PowerUp): pass