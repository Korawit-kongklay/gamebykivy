# นำเข้าโมดูลที่จำเป็นสำหรับกระสุน
from kivy.uix.widget import Widget  # คลาสพื้นฐานสำหรับกระสุน
from kivy.properties import NumericProperty, ReferenceListProperty  # คุณสมบัติสำหรับจัดการความเร็ว
from kivy.vector import Vector  # คลาสสำหรับจัดการเวกเตอร์
import math  # ใช้คำนวณทิศทางกระสุน

class Bullet(Widget):
    velocity_x = NumericProperty(0)  # ความเร็วแนวนอนของกระสุน
    velocity_y = NumericProperty(0)  # ความเร็วแนวตั้งของกระสุน
    velocity = ReferenceListProperty(velocity_x, velocity_y)  # รวมความเร็วทั้งสองแกน
    bullet_rotation = NumericProperty(0)  

    def __init__(self, start_pos, target_pos, **kwargs):
        super().__init__(**kwargs)
        self.size = (20, 5)
        self.pos = start_pos
        
        # คำนวณทิศทางไปยังเคอร์เซอร์
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        speed = 10
        
        if distance > 0:
            self.velocity_x = (dx / distance) * speed
            self.velocity_y = (dy / distance) * speed
            # คำนวณการหมุนทันทีเมื่อสร้างกระสุน
            self.bullet_rotation = math.degrees(math.atan2(dy, dx))

    def move(self):
        self.pos = Vector(self.velocity_x, self.velocity_y) + self.pos
        # อัพเดทการหมุนตามทิศทางการเคลื่อนที่
        self.update_rotation(self.velocity_x, self.velocity_y)

    def update_rotation(self, dx, dy):
        # คำนวณมุมจากการเคลื่อนที่
        angle = math.degrees(math.atan2(dy, dx))
        self.bullet_rotation = angle