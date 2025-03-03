from kivy.uix.widget import Widget

class Obstacle(Widget):
    def move(self):
        self.x -= 3  # ความเร็วสิ่งกีดขวาง