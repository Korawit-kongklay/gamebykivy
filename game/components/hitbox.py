from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty

class Hitbox:
    def __init__(self, offset_x=0, offset_y=0, width=0, height=0):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.width = width
        self.height = height

    def get_rect(self, parent_x, parent_y):
        return {
            'x': parent_x + self.offset_x,
            'y': parent_y + self.offset_y,
            'width': self.width,
            'height': self.height,
            'right': parent_x + self.offset_x + self.width,
            'top': parent_y + self.offset_y + self.height
        }

    @staticmethod
    def collide(rect1, rect2):
        return (rect1['x'] < rect2['right'] and
                rect1['right'] > rect2['x'] and
                rect1['y'] < rect2['top'] and
                rect1['top'] > rect2['y'])