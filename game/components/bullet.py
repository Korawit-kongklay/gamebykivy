# bullet.py
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector

class Bullet(Widget):
    velocity_x = NumericProperty(5)  # ความเร็วกระสุน
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def __init__(self, start_pos, **kwargs):
        super().__init__(**kwargs)
        self.size = (20, 5)  # ขนาดกระสุน
        self.pos = start_pos  # เริ่มจากตำแหน่งที่กำหนด

    def move(self):
        self.pos = Vector(self.velocity_x, 0) + self.pos