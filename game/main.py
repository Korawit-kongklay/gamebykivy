import random
import numpy as np
from scipy.spatial import Voronoi
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Triangle
from kivy.core.window import Window

class MapWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.generate_map)
        self.size = Window.size
        self.generate_map()

    def generate_map(self, *args):
        if self.width < 100 or self.height < 100:
            return

        self.canvas.clear()
        num_regions = 40  # จำนวนรัฐหรือประเทศ

        # กำหนดศูนย์กลางและรัศมีของ "ทวีป" เพื่อจำกัดจุด
        center_x, center_y = self.width / 2, self.height / 2
        max_radius_x, max_radius_y = self.width * 0.4, self.height * 0.4

        # สร้างจุดในขอบเขตวงรี (ellipse) เพื่อให้ดูเป็นทวีป
        points = []
        for _ in range(num_regions):
            while True:
                # สุ่มมุมและรัศมีในวงรี
                angle = random.uniform(0, 2 * np.pi)
                r_x = random.uniform(0, max_radius_x)
                r_y = random.uniform(0, max_radius_y)
                x = center_x + r_x * np.cos(angle)
                y = center_y + r_y * np.sin(angle)

                # ตรวจสอบระยะห่างขั้นต่ำจากจุดอื่น
                new_point = [x, y]
                if all(np.linalg.norm(np.array(new_point) - np.array(p)) > 30 for p in points):
                    points.append(new_point)
                    break
        points = np.array(points)

        try:
            vor = Voronoi(points)
        except Exception as e:
            print(f"Error creating Voronoi: {e}")
            return

        with self.canvas:
            # วาดและเติมสีให้แต่ละรัฐ
            for i, region in enumerate(vor.regions):
                if not -1 in region and len(region) > 2:
                    # สุ่มสีสำหรับแต่ละรัฐ
                    Color(random.random(), random.random(), random.random(), 1)

                    # รวบรวมจุดของขอบเขตและจำกัดให้อยู่ในวงรี
                    vertices = []
                    for idx in region:
                        x, y = vor.vertices[idx]
                        # ตรวจสอบว่าจุดอยู่ในวงรีหรือไม่
                        if ((x - center_x) / max_radius_x) ** 2 + ((y - center_y) / max_radius_y) ** 2 <= 1.2:  # ขยายขอบเขตเล็กน้อย
                            vertices.append([x, y])
                        else:
                            # ถ้าจุดอยู่นอกวงรี ให้ตัดทิ้งหรือปรับให้อยู่ขอบวงรี
                            direction = np.arctan2(y - center_y, x - center_x)
                            x = center_x + max_radius_x * np.cos(direction)
                            y = center_y + max_radius_y * np.sin(direction)
                            vertices.append([x, y])

                    # แปลงเป็นพิกัดสำหรับการวาด
                    points_list = []
                    for x, y in vertices:
                        x = max(0, min(x, self.width))
                        y = max(0, min(y, self.height))
                        points_list.extend([x, y])

                    # แบ่งเป็นสามเหลี่ยมเพื่อเติมสี
                    if len(points_list) >= 6:
                        for j in range(2, len(points_list) // 2):
                            triangle = [
                                points_list[0], points_list[1],
                                points_list[j * 2 - 2], points_list[j * 2 - 1],
                                points_list[j * 2], points_list[j * 2 + 1]
                            ]
                            Triangle(points=triangle)

                    # วาดเส้นขอบ
                    points_list.append(points_list[0])
                    points_list.append(points_list[1])
                    Color(0, 0, 0, 1)  # ขอบสีดำ
                    Line(points=points_list, width=2)

class RiskGame(App):
    def build(self):
        return MapWidget()

if __name__ == "__main__":
    Window.size = (800, 600)  # ปรับขนาดหน้าต่างให้ใหญ่ขึ้น
    RiskGame().run()