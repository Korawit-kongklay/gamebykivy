from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
import random

# คลาสสำหรับไดโนเสาร์
class Dino(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(0, self.velocity_y) + self.pos
        if self.y < 0:
            self.y = 0
            self.velocity_y = 0

# คลาสสำหรับสิ่งกีดขวาง
class Obstacle(Widget):
    def move(self):
        self.x -= 3  # ความเร็วสิ่งกีดขวาง

# คลาสหลักของเกม
class DinoGame(Widget):
    game_active = BooleanProperty(True)  # เปลี่ยนเป็น BooleanProperty
    dino = ObjectProperty(None)
    score = NumericProperty(0)
    obstacles = []  # รายการสิ่งกีดขวาง

    def __init__(self, **kwargs):
        super(DinoGame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.spawn_obstacle()  # เพิ่มสิ่งกีดขวางแรก

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar' and self.dino.y == 0:
            self.dino.velocity_y = 10
        return True

    def spawn_obstacle(self):
        # สร้างสิ่งกีดขวางใหม่
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

        # อัปเดตไดโนเสาร์
        self.dino.velocity_y -= 0.10
        self.dino.move()

        # อัปเดตสิ่งกีดขวาง
        for obstacle in self.obstacles[:]:
            obstacle.move()
            if obstacle.x < -obstacle.width:
                self.remove_widget(obstacle)
                self.obstacles.remove(obstacle)
                self.score += 1

            # ตรวจจับการชน
            if self.dino.collide_widget(obstacle):
                self.game_over()

        # สุ่มเพิ่มสิ่งกีดขวางใหม่
        if random.random() < 0.02:
            self.spawn_obstacle()

    def game_over(self):
        self.game_active = False  # อัปเดตสถานะ
        for obstacle in self.obstacles:
            self.remove_widget(obstacle)
        self.obstacles.clear()
        Clock.unschedule(self.update)

    def restart(self):
        self.game_active = True
        self.score = 0
        self.obstacles.clear()
        self.spawn_obstacle()
        Clock.schedule_interval(self.update, 1.0 / 60.0)

# แอปหลัก
class DinoApp(App):
    def build(self):
        game = DinoGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    DinoApp().run()