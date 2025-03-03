from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
import random
from dino import Dino
from obstacle import Obstacle

class DinoGame(Widget):
    game_active = BooleanProperty(True)
    dino = ObjectProperty(None)
    score = NumericProperty(0)
    obstacles = []
    bullets = []  # เพิ่มลิสต์สำหรับกระสุน

    def __init__(self, **kwargs):
        super(DinoGame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.spawn_obstacle()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar' and self.dino.y == 0:
            self.dino.velocity_y = 10
        return True

    def spawn_obstacle(self):
        obstacle = Obstacle()
        min_distance = 500
        obstacle.x = self.width + min_distance + random.randint(0, 300)
        obstacle.y = 0
        self.add_widget(obstacle)
        self.obstacles.append(obstacle)

    def update(self, dt):
        if not self.game_active:
            return
        if self.dino is None:
            print("Error: Dino not initialized!")
            return

        self.dino.velocity_y -= 0.10
        self.dino.move()

        # อัปเดตสิ่งกีดขวาง (วางโค้ดที่นี่)
        for obstacle in self.obstacles[:]:
            obstacle.move()
            if obstacle.x < -obstacle.width:
                self.remove_widget(obstacle)
                self.obstacle