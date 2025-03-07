from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
import random
from .dino import Dino
from .obstacle import Obstacle
from .bullet import Bullet

# คลาสสำหรับบอส
class Boss(Obstacle):
    health = NumericProperty(3)  # พลังชีวิตบอส

    def move(self):
        self.x -= 1  # บอสเคลื่อนที่ช้ากว่า

class DinoGame(Widget):
    game_active = BooleanProperty(True)
    dino = ObjectProperty(None)
    score = NumericProperty(0)
    stage = NumericProperty(1)
    obstacles_to_clear = NumericProperty(10)
    obstacles_cleared = NumericProperty(0)
    obstacles = []
    bullets = []
    
    # ตัวแปรปรับแต่ง
    spawn_frequency = NumericProperty(0.02)  # ความถี่การเกิดอุปสรรค (0.02 = 2% ต่อเฟรม)
    min_spawn_distance = NumericProperty(150)  # ระยะห่างขั้นต่ำระหว่างอุปสรรค
    shoot_cooldown = NumericProperty(0.5)  # วินาทีที่ต้องรอก่อนยิงครั้งต่อไป
    last_shot_time = NumericProperty(0)  # เวลาที่บันทึกการยิงล่าสุด

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
            current_time = Clock.get_time()  # รับเวลาปัจจุบัน
            if current_time - self.last_shot_time >= self.shoot_cooldown:  # ตรวจสอบ cooldown
                start_pos = (self.dino.x + self.dino.width, self.dino.y + self.dino.height / 2)
                bullet = Bullet(start_pos=start_pos)
                self.add_widget(bullet)
                self.bullets.append(bullet)
                self.last_shot_time = current_time  # อัปเดตเวลาการยิง
        return True

    def spawn_obstacle(self):
        # ตรวจสอบระยะห่างจากอุปสรรคตัวล่าสุด
        if self.obstacles:
            last_obstacle = self.obstacles[-1]
            if self.width - last_obstacle.x < self.min_spawn_distance:
                return  # ไม่เกิดถ้าระยะห่างน้อยเกินไป

        # ทุกด่านที่ 3 มีบอส ถ้ายังไม่มีบอสในฉาก
        if self.stage % 3 == 0 and not any(isinstance(o, Boss) for o in self.obstacles):
            obstacle = Boss()
        else:
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

        # อัปเดตกระสุน
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.x > self.width:
                self.remove_widget(bullet)
                self.bullets.remove(bullet)

        # อัปเดตสิ่งกีดขวางและบอส
        for obstacle in self.obstacles[:]:
            obstacle.move()
            if obstacle.x < -obstacle.width:
                self.remove_widget(obstacle)
                self.obstacles.remove(obstacle)
                self.score += 1
                self.obstacles_cleared += 1

            for bullet in self.bullets[:]:
                if bullet.collide_widget(obstacle):
                    if isinstance(obstacle, Boss):
                        obstacle.health -= 1
                        if obstacle.health <= 0:
                            self.remove_widget(obstacle)
                            self.obstacles.remove(obstacle)
                            self.score += 20
                            self.obstacles_cleared += 1
                    else:
                        self.remove_widget(obstacle)
                        self.obstacles.remove(obstacle)
                        self.score += 5
                        self.obstacles_cleared += 1
                    self.remove_widget(bullet)
                    self.bullets.remove(bullet)
                    break

            if self.dino.collide_widget(obstacle):
                self.game_over()

        # ไปด่านต่อไปหรือเพิ่มศัตรู
        if self.obstacles_cleared >= self.obstacles_to_clear:
            self.next_stage()
        elif len(self.obstacles) < 3 and random.random() < self.spawn_frequency:
            self.spawn_obstacle()

    def next_stage(self):
        self.stage += 1
        self.obstacles_cleared = 0
        self.obstacles.clear()
        if self.stage <= 5:
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
        self.last_shot_time = 0  # รีเซ็ตเวลา cooldown
        self.spawn_obstacle()
        Clock.schedule_interval(self.update, 1.0 / 60.0)