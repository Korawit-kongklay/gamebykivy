# components/dino_game.py
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
import random
from .dino import Dino
from .obstacle import Obstacle
from .bullet import Bullet

class DinoGame(Widget):
    game_active = BooleanProperty(True)
    dino = ObjectProperty(None)
    score = NumericProperty(0)
    stage = NumericProperty(1)
    obstacles_to_clear = NumericProperty(10)  # จำนวนสิ่งกีดขวางที่ต้องเคลียร์ต่อด่าน
    obstacles_cleared = NumericProperty(0)
    obstacles = []
    bullets = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.spawn_obstacle()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar' and self.dino.y == 0:
            self.dino.velocity_y = 10
        elif keycode[1] == 'b' and self.game_active:
            start_pos = (self.dino.x + self.dino.width, self.dino.y + self.dino.height / 2)
            bullet = Bullet(start_pos=start_pos)
            self.add_widget(bullet)
            self.bullets.append(bullet)
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

        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.x > self.width:
                self.remove_widget(bullet)
                self.bullets.remove(bullet)

        for obstacle in self.obstacles[:]:
            obstacle.move()
            if obstacle.x < -obstacle.width:
                self.remove_widget(obstacle)
                self.obstacles.remove(obstacle)
                self.score += 1
                self.obstacles_cleared += 1

            for bullet in self.bullets[:]:
                if bullet.collide_widget(obstacle):
                    self.remove_widget(obstacle)
                    self.remove_widget(bullet)
                    self.obstacles.remove(obstacle)
                    self.bullets.remove(bullet)
                    self.score += 5
                    self.obstacles_cleared += 1
                    break

            if self.dino.collide_widget(obstacle):
                self.game_over()

        if self.obstacles_cleared >= self.obstacles_to_clear:
            self.next_stage()
        elif len(self.obstacles) < 3:  # จำกัดจำนวนสิ่งกีดขวางในด่าน
            self.spawn_obstacle()

    def next_stage(self):
        self.stage += 1
        self.obstacles_cleared = 0
        self.obstacles.clear()
        if self.stage <= 5:  # จำกัด 5 ด่าน
            self.spawn_obstacle()
        else:
            self.game_active = False  # ชนะเกม

    def game_over(self):
        self.game_active = False
        for obstacle in self.obstacles:
            self.remove_widget(obstacle)
        for bullet in self.bullets:
            self.remove_widget(bullet)
        self.obstacles.clear()
        self.bullets.clear()
        Clock.unschedule(self.update)

    def restart(self):
        self.game_active = True
        self.score = 0
        self.stage = 1
        self.obstacles_cleared = 0
        self.obstacles.clear()
        self.bullets.clear()
        self.spawn_obstacle()
        Clock.schedule_interval(self.update, 1.0 / 60.0)