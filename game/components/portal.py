from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse

class Portal(Widget):
    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, 50)
        self.pos = pos
        with self.canvas:
            Color(0, 1, 1, 1)  # สีฟ้า
            Ellipse(pos=self.pos, size=self.size)

    def get_hitbox_rect(self):
        """Return hitbox rectangle for collision detection."""
        return {
            'x': self.x,
            'y': self.y,
            'right': self.x + self.width,
            'top': self.y + self.height
        }