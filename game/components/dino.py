# นำเข้าโมดูลและคลาสที่จำเป็นสำหรับจัดการไดโนเสาร์
from kivy.uix.widget import Widget  # คลาสพื้นฐานสำหรับสร้างวัตถุในเกม (เช่น ไดโน)
from kivy.properties import NumericProperty, ReferenceListProperty  # คุณสมบัติสำหรับจัดการค่าตัวเลขและลิสต์ใน Kivy
from kivy.vector import Vector  # คลาสสำหรับจัดการเวกเตอร์ (ตำแหน่งและความเร็ว)

# คลาสสำหรับไดโนเสาร์ (ตัวละครหลักของเกม)
class Dino(Widget):
    velocity_x = NumericProperty(0)  # ความเร็วในแนวนอนของไดโน (เริ่มต้นที่ 0)
    velocity_y = NumericProperty(0)  # ความเร็วในแนวตั้งของไดโน (เริ่มต้นที่ 0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)  # รวม velocity_x และ velocity_y เป็นลิสต์ (สำหรับใช้งานง่าย)

    def move(self):  # ฟังก์ชันจัดการการเคลื่อนที่ของไดโน
        self.pos = Vector(0, self.velocity_y) + self.pos  # อัปเดตตำแหน่งโดยเพิ่มความเร็วแนวตั้ง (x ไม่เปลี่ยน)
        if self.y < 0:  # ถ้าตำแหน่ง y ต่ำกว่าพื้น (0)
            self.y = 0  # ปรับตำแหน่งให้อยู่ที่พื้น
            self.velocity_y = 0  # หยุดความเร็วแนวตั้ง (ป้องกันการตกลงไปใต้พื้น)