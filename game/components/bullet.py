from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
import math

class BaseBullet(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    bullet_rotation = NumericProperty(0)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PlayerBullet(BaseBullet):
    def __init__(self, start_pos: tuple, target_pos: tuple, speed: float = 10, **kwargs):
        super().__init__(**kwargs)
        self.size = (20, 5)
        self.pos = start_pos
        
        dx, dy = target_pos[0] - start_pos[0], target_pos[1] - start_pos[1]
        distance = max(math.sqrt(dx**2 + dy**2), 0.1)
        self.velocity_x = (dx / distance) * speed
        self.velocity_y = (dy / distance) * speed
        self.bullet_rotation = math.degrees(math.atan2(dy, dx))

class BossBullet(BaseBullet):
    def __init__(self, start_pos: tuple, **kwargs):
        super().__init__(**kwargs)
        self.size = (15, 15)
        self.pos = start_pos
        self.velocity_x = -5

    def move(self):
        self.x -= 5