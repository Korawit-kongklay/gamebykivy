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
    health = NumericProperty(3)
    def move(self):
        self.x -= 1

# คลาสสำหรับ Power-Ups
class SpeedPowerUp(Widget):
    pass

class ShieldPowerUp(Widget):
    pass

class AmmoPowerUp(Widget):
    pass

class HealthPowerUp(Widget):
    pass

class ScorePowerUp(Widget):
    pass

class DinoGame(Widget):
    game_active = BooleanProperty(True)
    dino = ObjectProperty(None)
    score = NumericProperty(0)
    stage = NumericProperty(1)
    obstacles_to_clear = NumericProperty(10)
    obstacles_cleared = NumericProperty(0)
    obstacles = []
    bullets = []
    power_ups = []  # ลิสต์สำหรับ Power-Ups
    health = NumericProperty(3)  # เพิ่มชีวิตไดโน (ใช้กับ HealthPowerUp)
    shield_active = BooleanProperty(False)  # สถานะโล่ (ใช้กับ ShieldPowerUp)
    
    # ตัวแปรปรับแต่ง
    spawn_frequency = NumericProperty(0.02)
    min_spawn_distance = NumericProperty(150)
    shoot_cooldown = NumericProperty(0.5)
    last_shot_time = NumericProperty(0)

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
            current_time = Clock.get_time()
            if current_time - self.last_shot_time >= self.shoot_cooldown:
                start_pos = (self.dino.x + self.dino.width, self.dino.y + self.dino.height / 2)
                bullet = Bullet(start_pos=start_pos)
                self.add_widget(bullet)
                self.bullets.append(bullet)
                self.last_shot_time = current_time
        return True

    def spawn_obstacle(self):
        if self.obstacles and self.width - self.obstacles[-1].x < self.min_spawn_distance:
            return
        if self.stage % 3 == 0 and not any(isinstance(o, Boss) for o in self.obstacles):
            obstacle = Boss()
        else:
            obstacle = Obstacle()
        obstacle.x = self.width + 500 + random.randint(0, 300)
        obstacle.y = 0
        self.add_widget(obstacle)
        self.obstacles.append(obstacle)

    def spawn_power_up(self):
        if random.random() < 0.01:  # 1% ต่อเฟรม
            power_up_types = [SpeedPowerUp, ShieldPowerUp, AmmoPowerUp, HealthPowerUp, ScorePowerUp]
            power_up = random.choice(power_up_types)()
            power_up.x = self.width + random.randint(0, 300)
            power_up.y = random.randint(50, 200)  # 浮อยู่ในอากาศ
            self.add_widget(power_up)
            self.power_ups.append(power_up)

    def collect_power_up(self, power_up):
        if isinstance(power_up, SpeedPowerUp):
            self.dino.velocity_x = 2  # เพิ่มความเร็วชั่วคราว
            Clock.schedule_once(lambda dt: self.reset_speed(), 5)  # รีเซ็ตหลัง 5 วินาที
        elif isinstance(power_up, ShieldPowerUp):
            self.shield_active = True
            Clock.schedule_once(lambda dt: self.reset_shield(), 10)  # โล่หมดหลัง 10 วินาที
        elif isinstance(power_up, AmmoPowerUp):
            self.shoot_cooldown = max(0.1, self.shoot_cooldown - 0.2)  # ลด cooldown
        elif isinstance(power_up, HealthPowerUp):
            self.health = min(5, self.health + 1)  # เพิ่มชีวิต (สูงสุด 5)
        elif isinstance(power_up, ScorePowerUp):
            self.score += 50  # คะแนนพิเศษ
        self.remove_widget(power_up)
        self.power_ups.remove(power_up)

    def reset_speed(self):
        self.dino.velocity_x = 0  # รีเซ็ตความเร็ว

    def reset_shield(self):
        self.shield_active = False  # รีเซ็ตโล่

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
                if self.shield_active:
                    self.shield_active = False
                else:
                    self.health -= 1
                    if self.health <= 0:
                        self.game_over()

        for power_up in self.power_ups[:]:
            if self.dino.collide_widget(power_up):
                self.collect_power_up(power_up)

        if self.obstacles_cleared >= self.obstacles_to_clear:
            self.next_stage()
        elif len(self.obstacles) < 3 and random.random() < self.spawn_frequency:
            self.spawn_obstacle()
        self.spawn_power_up()

    def next_stage(self):
        self.stage += 1
        self.obstacles_cleared = 0
        self.obstacles.clear()
        if self.stage <= 5:
            self.spawn_obstacle()
        else:
            self.game_active = False

    def game_over(self):
        self.game_active = False
        for obstacle in self.obstacles:
            self.remove_widget(obstacle)
        for bullet in self.bullets:
            self.remove_widget(bullet)
        for power_up in self.power_ups:
            self.remove_widget(power_up)
        self.obstacles.clear()
        self.bullets.clear()
        self.power_ups.clear()
        Clock.unschedule(self.update)

    def restart(self):
        self.game_active = True
        self.score = 0
        self.stage = 1
        self.obstacles_cleared = 0
        self.health = 3
        self.shield_active = False
        self.shoot_cooldown = 0.5
        self.obstacles.clear()
        self.bullets.clear()
        self.power_ups.clear()
        self.last_shot_time = 0
        self.spawn_obstacle()
        Clock.schedule_interval(self.update, 1.0 / 60.0)