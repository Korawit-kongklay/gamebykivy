# นำเข้าโมดูลที่จำเป็นสำหรับกระสุน
from kivy.uix.widget import Widget  # คลาสพื้นฐานสำหรับกระสุน
from kivy.properties import NumericProperty, ReferenceListProperty  # คุณสมบัติสำหรับจัดการความเร็ว
from kivy.vector import Vector  # คลาสสำหรับจัดการเวกเตอร์
import math  # ใช้คำนวณทิศทางกระสุน

class Bullet(Widget):
    velocity_x = NumericProperty(0)  # ความเร็วแนวนอนของกระสุน
    velocity_y = NumericProperty(0)  # ความเร็วแนวตั้งของกระสุน
    velocity = ReferenceListProperty(velocity_x, velocity_y)  # รวมความเร็วทั้งสองแกน

    def __init__(self, start_pos, target_pos, **kwargs):  # ฟังก์ชันเริ่มต้นกระสุน
        super().__init__(**kwargs)
        self.size = (20, 5)  # กำหนดขนาดกระสุน
        self.pos = start_pos  # ตำแหน่งเริ่มต้น (จากไดโน)
        # คำนวณทิศทางไปยังเคอร์เซอร์
        dx = target_pos[0] - start_pos[0]  # ระยะห่างในแกน x
        dy = target_pos[1] - start_pos[1]  # ระยะห่างในแกน y
        distance = math.sqrt(dx**2 + dy**2)  # คำนวณระยะทางรวม
        speed = 10  # ความเร็วกระสุน
        if distance > 0:  # ป้องกันการหารด้วย 0
            self.velocity_x = (dx / distance) * speed  # ความเร็ว x ตามทิศทาง
            self.velocity_y = (dy / distance) * speed  # ความเร็ว y ตามทิศทาง

    def move(self):  # เมธอดเคลื่อนที่กระสุน
        self.pos = Vector(self.velocity_x, self.velocity_y) + self.pos  # อัปเดตตำแหน่งตามความเร็ว