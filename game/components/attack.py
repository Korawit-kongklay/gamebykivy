from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
import math
from .hitbox import Hitbox

class Attack(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    attack_rotation = NumericProperty(0)
    hitbox = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hitbox = Hitbox(offset_x=0, offset_y=0, width=self.size[0], height=self.size[1])

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def get_hitbox_rect(self):
        return self.hitbox.get_rect(self.x, self.y)

class ProjectileAttack(Attack):
    def __init__(self, start_pos: tuple, target_pos: tuple, speed: float = 10, **kwargs):
        super().__init__(**kwargs)
        self.size = (20, 5)
        self.pos = start_pos
        self.hitbox = Hitbox(offset_x=0, offset_y=0, width=20, height=5)
        
        dx, dy = target_pos[0] - start_pos[0], target_pos[1] - start_pos[1]
        distance = max(math.sqrt(dx**2 + dy**2), 0.1)
        self.velocity_x = (dx / distance) * speed
        self.velocity_y = (dy / distance) * speed
        self.attack_rotation = math.degrees(math.atan2(dy, dx))

class EnemyProjectile(Attack):
    def __init__(self, start_pos: tuple, **kwargs):
        super().__init__(**kwargs)
        self.size = (15, 15)
        self.pos = start_pos
        self.hitbox = Hitbox(offset_x=0, offset_y=0, width=15, height=15)
        self.velocity_x = -5

    def move(self):
        self.x -= 5