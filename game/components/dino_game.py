# นำเข้าโมดูลและคลาสที่จำเป็นสำหรับการสร้างเกม
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
import random
from .dino import Dino
from .obstacle import Obstacle
from .bullet import Bullet

# คลาสสำหรับบอส (หัวหน้านักรบ)
class Boss(Obstacle):
    health = NumericProperty(3)  # พลังชีวิตของบอสเริ่มต้นที่ 3
    def move(self):  # เมธอดสำหรับเคลื่อนที่บอส
        self.x -= 1  # เคลื่อนที่ไปทางซ้ายช้ากว่าศัตรูปกติ
    def shoot(self, game):  # ฟังก์ชันให้บอสยิงกระสุน
        bullet = BossBullet()
        bullet.pos = (self.x - bullet.width, self.y + self.height / 2)  # กระสุนเริ่มจากด้านหน้าบอส
        game.add_widget(bullet)
        game.boss_bullets.append(bullet)

# คลาสสำหรับกระสุนของบอส
class BossBullet(Widget):
    def move(self):  # เมธอดเคลื่อนที่กระสุน
        self.x -= 5  # เคลื่อนที่ไปทางซ้าย (เร็วขึ้นเล็กน้อย)

# คลาสสำหรับ Power-Ups (ไอเทมพิเศษ)
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

# คลาสหลักของเกม
class DinoGame(Widget):
    game_active = BooleanProperty(True)  # สถานะเกม (True = กำลังเล่น, False = จบ)
    dino = ObjectProperty(None)  # อ้างอิงถึงไดโนเสาร์
    score = NumericProperty(0)  # คะแนนของผู้เล่น
    stage = NumericProperty(1)  # ด่านปัจจุบัน (เริ่มที่ 1)
    obstacles_to_clear = NumericProperty(10)  # จำนวนศัตรูที่ต้องเคลียร์
    obstacles_cleared = NumericProperty(0)  # จำนวนศัตรูที่เคลียร์ไปแล้ว
    obstacles = []  # ลิสต์เก็บศัตรูและบอส
    bullets = []  # ลิสต์เก็บกระสุนของไดโน
    boss_bullets = []  # ลิสต์เก็บกระสุนของบอส
    power_ups = []  # ลิสต์เก็บ Power-Ups
    health = NumericProperty(3)  # พลังชีวิตของไดโน (3 หัวใจ, ไม่แสดง UI)
    shield_active = BooleanProperty(False)  # สถานะโล่
    
    # ตัวแปรปรับแต่ง
    spawn_frequency = NumericProperty(0.02)  # ความถี่การเกิดศัตรู (2% ต่อเฟรม)
    min_spawn_distance = NumericProperty(150)  # ระยะห่างขั้นต่ำระหว่างศัตรู
    shoot_cooldown = NumericProperty(0.5)  # ระยะเวลารอระหว่างการยิง (0.5 วินาที)
    last_shot_time = NumericProperty(0)  # บันทึกเวลาที่เพิ่งยิงกระสุนล่าสุด

    def __init__(self, **kwargs):  # ฟังก์ชันเริ่มต้นเมื่อสร้างอ็อบเจ็กต์ DinoGame
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)  # ขอคีย์บอร์ดจากระบบ
        self._keyboard.bind(on_key_down=self._on_keyboard_down)  # ผูกปุ่มกดกับฟังก์ชัน
        Window.bind(mouse_pos=self._on_mouse_pos)  # ผูกตำแหน่งเคอร์เซอร์เมาส์ (แก้จาก on_cursor_pos)
        Window.bind(on_mouse_down=self._on_mouse_down)  # ผูกการคลิกเมาส์
        self.mouse_pos = (0, 0)  # เก็บตำแหน่งเคอร์เซอร์เริ่มต้น (เปลี่ยนชื่อเป็น mouse_pos)
        self.spawn_obstacle()  # เริ่มต้นด้วยการสร้างศัตรูตัวแรก
        Clock.schedule_interval(self.update, 1.0 / 60.0)  # เริ่มอัปเดตเกมทันที (แก้ปัญหายิงไม่ออก)
        self.invincibility_timer = 0  # ตัวจับเวลาพ้นภัยเริ่มต้น

    def _keyboard_closed(self):  # ฟังก์ชันที่เรียกเมื่อคีย์บอร์ดถูกปิด
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)  # ยกเลิกการผูกปุ่มกด
        self._keyboard = None  # ล้างตัวแปรคีย์บอร์ด

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):  # ฟังก์ชันจัดการเมื่อกดปุ่ม
        if keycode[1] == 'spacebar' and self.dino.y == 0:  # ถ้ากด Spacebar และไดโนอยู่ที่พื้น
            self.dino.velocity_y = 5  # ทำให้ไดโนกระโดด
        return True  # บอกว่ารับคำสั่งเรียบร้อย

    def _on_mouse_pos(self, window, pos):  # ฟังก์ชันอัปเดตตำแหน่งเคอร์เซอร์ (แก้ชื่อจาก on_cursor_pos)
        self.mouse_pos = pos  # บันทึกตำแหน่งเคอร์เซอร์ปัจจุบัน

    def _on_mouse_down(self, window, x, y, button, modifiers):  # ฟังก์ชันจัดการเมื่อคลิกเมาส์
        if button == 'left' and self.game_active:  # ถ้าคลิกซ้ายและเกมยังดำเนินอยู่
            current_time = Clock.get_time()  # รับเวลาปัจจุบัน
            if current_time - self.last_shot_time >= self.shoot_cooldown:  # ตรวจสอบว่าเกิน Cooldown หรือยัง
                start_pos = (self.dino.x + self.dino.width, self.dino.y + self.dino.height / 2)  # ตำแหน่งเริ่มต้นกระสุน
                target_pos = self.mouse_pos  # ใช้ตำแหน่งเคอร์เซอร์ปัจจุบัน
                bullet = Bullet(start_pos=start_pos, target_pos=target_pos)  # สร้างกระสุนไปยังเคอร์เซอร์
                self.add_widget(bullet)  # เพิ่มกระสุนลงในฉาก
                self.bullets.append(bullet)  # เก็บกระสุนในลิสต์
                self.last_shot_time = current_time  # อัปเดตเวลาการยิงล่าสุด

    def spawn_obstacle(self):  # ฟังก์ชันสร้างศัตรูหรือบอส
        if self.obstacles and self.width - self.obstacles[-1].x < self.min_spawn_distance:  # ถ้ามีศัตรูและระยะห่างน้อยเกินไป
            return  # ไม่สร้างศัตรูใหม่
        if self.stage % 3 == 0 and not any(isinstance(o, Boss) for o in self.obstacles):  # ถ้าด่านหาร 3 ลงตัวและยังไม่มีบอส
            obstacle = Boss()  # สร้างบอส
            Clock.schedule_interval(lambda dt: obstacle.shoot(self), 2.0)  # บอสยิงทุก 2 วินาที
        else:
            obstacle = Obstacle()  # สร้างศัตรูปกติ
        obstacle.x = self.width + 500 + random.randint(0, 300)  # กำหนดตำแหน่ง x (นอกจอด้านขวา)
        obstacle.y = 0  # ตำแหน่ง y ที่พื้น
        self.add_widget(obstacle)  # เพิ่มศัตรูลงในฉาก
        self.obstacles.append(obstacle)  # เก็บศัตรูในลิสต์

    def spawn_power_up(self):  # ฟังก์ชันสร้าง Power-Up
        if random.random() < 0.01:  # มีโอกาส 1% ต่อเฟรม
            power_up_types = [SpeedPowerUp, ShieldPowerUp, AmmoPowerUp, HealthPowerUp, ScorePowerUp]  # ลิสต์ชนิด Power-Up
            power_up = random.choice(power_up_types)()  # สุ่มเลือกและสร้าง Power-Up
            power_up.x = self.width + random.randint(0, 300)  # ตำแหน่ง x นอกจอด้านขวา
            power_up.y = random.randint(50, 200)  # ตำแหน่ง y ลอยในอากาศ
            self.add_widget(power_up)  # เพิ่ม Power-Up ลงในฉาก
            self.power_ups.append(power_up)  # เก็บ Power-Up ในลิสต์

    def collect_power_up(self, power_up):  # ฟังก์ชันจัดการเมื่อไดโนเก็บ Power-Up
        if isinstance(power_up, SpeedPowerUp):  # ถ้าเป็น SpeedPowerUp
            self.dino.velocity_x = 2  # เพิ่มความเร็วแนวนอนชั่วคราว
            Clock.schedule_once(lambda dt: self.reset_speed(), 5)  # รีเซ็ตความเร็วหลัง 5 วินาที
        elif isinstance(power_up, ShieldPowerUp):  # ถ้าเป็น ShieldPowerUp
            self.shield_active = True  # เปิดใช้งานโล่
            Clock.schedule_once(lambda dt: self.reset_shield(), 10)  # ปิดโล่หลัง 10 วินาที
        elif isinstance(power_up, AmmoPowerUp):  # ถ้าเป็น AmmoPowerUp
            self.shoot_cooldown = max(0.1, self.shoot_cooldown - 0.2)  # ลด Cooldown (ขั้นต่ำ 0.1)
        elif isinstance(power_up, HealthPowerUp):  # ถ้าเป็น HealthPowerUp
            self.health = min(5, self.health + 1)  # เพิ่มชีวิต (สูงสุด 5)
        elif isinstance(power_up, ScorePowerUp):  # ถ้าเป็น ScorePowerUp
            self.score += 50  # เพิ่มคะแนน 50
        self.remove_widget(power_up)  # ลบ Power-Up ออกจากฉาก
        self.power_ups.remove(power_up)  # ลบ Power-Up ออกจากลิสต์

    def reset_speed(self):  # ฟังก์ชันรีเซ็ตความเร็วของไดโน
        self.dino.velocity_x = 0  # กลับสู่ความเร็วปกติ

    def reset_shield(self):  # ฟังก์ชันรีเซ็ตสถานะโล่
        self.shield_active = False  # ปิดการใช้งานโล่

    def update(self, dt):  # ฟังก์ชันอัปเดตเกมทุกเฟรม
        if not self.game_active:
            return
        if self.dino is None:
            print("Error: Dino not initialized!")
            return

        self.dino.velocity_y -= 0.10  # ลดความเร็วแนวตั้ง (แรงโน้มถ่วง)
        self.dino.move()  # อัปเดตตำแหน่งไดโน

        # ลดตัวจับเวลาพ้นภัย
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt  # ลดตามเวลาจริง (dt = delta time)

        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.x > self.width or bullet.y > self.height or bullet.x < 0 or bullet.y < 0:
                self.remove_widget(bullet)
                self.bullets.remove(bullet)

        for bullet in self.boss_bullets[:]:
            bullet.move()
            if bullet.x < -bullet.width:
                self.remove_widget(bullet)
                self.boss_bullets.remove(bullet)
            if self.dino.collide_widget(bullet) and self.invincibility_timer <= 0:  # ถ้ากระสุนบอสชนไดโน และไม่อยู่ในช่วงพ้นภัย
                self.remove_widget(bullet)
                self.boss_bullets.remove(bullet)
                if self.shield_active:
                    self.shield_active = False
                else:
                    self.health -= 1  # ลดพลังชีวิต 1 หัวใจ
                    print(f"Health left: {self.health}")  # ดีบั๊ก
                    self.invincibility_timer = 0.5  # ตั้งเวลาพ้นภัย 0.5 วินาที
                    if self.health <= 0:
                        self.game_over()

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

            if self.dino.collide_widget(obstacle) and self.invincibility_timer <= 0:  # ถ้าไดโนชนศัตรู และไม่อยู่ในช่วงพ้นภัย
                self.remove_widget(obstacle)  # ลบศัตรูทันทีเมื่อชน
                self.obstacles.remove(obstacle)  # ลบออกจากลิสต์
                if self.shield_active:  # ถ้ามีโล่
                    self.shield_active = False  # ใช้โล่และปิด
                else:  # ถ้าไม่มีโล่
                    self.health -= 1  # ลดพลังชีวิต 1 หัวใจ
                    print(f"Health left: {self.health}")  # ดีบั๊ก
                    self.invincibility_timer = 0.5  # ตั้งเวลาพ้นภัย 0.5 วินาที
                    if self.health <= 0:  # ถ้าพลังชีวิตหมด
                        self.game_over()  # จบเกม

        for power_up in self.power_ups[:]:
            if self.dino.collide_widget(power_up):
                self.collect_power_up(power_up)

        if self.obstacles_cleared >= self.obstacles_to_clear:
            self.next_stage()
        elif len(self.obstacles) < 3 and random.random() < self.spawn_frequency:
            self.spawn_obstacle()
        self.spawn_power_up()

    def next_stage(self):  # ฟังก์ชันไปด่านต่อไป
        self.stage += 1  # เพิ่มด่าน
        self.obstacles_cleared = 0  # รีเซ็ตจำนวนที่เคลียร์
        self.obstacles.clear()  # ล้างศัตรูทั้งหมด
        if self.stage <= 5:  # ถ้ายังไม่ถึงด่าน 6
            self.spawn_obstacle()  # สร้างศัตรูใหม่
        else:  # ถ้าถึงด่าน 6
            self.game_active = False  # ชนะเกม

    def game_over(self):  # ฟังก์ชันจบเกม
        self.game_active = False  # หยุดเกม
        for obstacle in self.obstacles:  # ลบศัตรูทั้งหมด
            self.remove_widget(obstacle)
        for bullet in self.bullets:  # ลบกระสุนของไดโนทั้งหมด
            self.remove_widget(bullet)
        for bullet in self.boss_bullets:  # ลบกระสุนของบอสทั้งหมด
            self.remove_widget(bullet)
        for power_up in self.power_ups:  # ลบ Power-Ups ทั้งหมด
            self.remove_widget(power_up)
        self.obstacles.clear()  # ล้างลิสต์ศัตรู
        self.bullets.clear()  # ล้างลิสต์กระสุนของไดโน
        self.boss_bullets.clear()  # ล้างลิสต์กระสุนของบอส
        self.power_ups.clear()  # ล้างลิสต์ Power-Ups
        Clock.unschedule(self.update)  # หยุดการอัปเดต

    def restart(self):  # ฟังก์ชันเริ่มเกมใหม่
        self.game_active = True
        self.score = 0
        self.stage = 1
        self.obstacles_cleared = 0
        self.health = 3  # รีเซ็ตพลังชีวิตเป็น 3 หัวใจ
        self.shield_active = False
        self.invincibility_timer = 0  # รีเซ็ตตัวจับเวลาพ้นภัย
        self.shoot_cooldown = 0.5
        self.obstacles.clear()
        self.bullets.clear()
        self.boss_bullets.clear()
        self.power_ups.clear()
        self.last_shot_time = 0
        self.spawn_obstacle()
        Clock.schedule_interval(self.update, 1.0 / 60.0)