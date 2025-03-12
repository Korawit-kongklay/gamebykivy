from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
import random
from .dino import Dino
from .boss import Boss, BossBullet
from .obstacle import Obstacle
from .bullet import Bullet
from .powerup import SpeedPowerUp, ShieldPowerUp, AmmoPowerUp, HealthPowerUp, ScorePowerUp, PowerUp
from .stage import Stage

class DinoGame(Widget):
    dino = ObjectProperty(None)
    stage = ObjectProperty(None)
    score = NumericProperty(0)
    stage_number = NumericProperty(1)
    obstacles_cleared = NumericProperty(0)
    obstacles_to_clear = NumericProperty(10)
    health = NumericProperty(3)
    shield_active = BooleanProperty(False)
    game_active = BooleanProperty(True)
    bullets = ListProperty([])
    boss_bullets = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stage = Stage(stage_number=self.stage_number)
        self.keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self.keyboard.bind(on_key_down=self._on_keyboard_down)
        self.keyboard.bind(on_key_up=self._on_keyboard_up)
        Window.bind(mouse_pos=self._on_mouse_pos, on_mouse_down=self._on_mouse_down)
        self.mouse_pos = (0, 0)
        self.invincibility_timer = 0
        self.shoot_cooldown = 0.5
        self.last_shot_time = 0
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def _keyboard_closed(self) -> None:
        self.keyboard.unbind(on_key_down=self._on_keyboard_down)
        self.keyboard.unbind(on_key_up=self._on_keyboard_up)
        self.keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers) -> bool:
        if not self.game_active:
            return False
        if keycode[1] == 'spacebar' and self.dino.y == 0:
            self.dino.velocity_y = 5
        elif keycode[1] in ('left', 'a'):
            self.dino.velocity_x = -3
        elif keycode[1] in ('right', 'd'):
            self.dino.velocity_x = 3
        return True

    def _on_keyboard_up(self, keyboard, keycode) -> bool:
        if keycode[1] in ('left', 'a', 'right', 'd'):
            self.dino.velocity_x = 0
        return True

    def _on_mouse_pos(self, window, pos) -> None:
        self.mouse_pos = pos

    def _on_mouse_down(self, window, x, y, button, modifiers) -> None:
        if button != 'left' or not self.game_active:
            return
        current_time = Clock.get_time()
        if current_time - self.last_shot_time < self.shoot_cooldown:
            return
        
        start_pos = (self.dino.x + self.dino.width, self.dino.y + self.dino.height / 2)
        bullet = Bullet(start_pos=start_pos, target_pos=self.mouse_pos)
        self.add_widget(bullet)
        self.bullets.append(bullet)
        self.last_shot_time = current_time

    def collect_power_up(self, power_up: PowerUp) -> None:
        if isinstance(power_up, SpeedPowerUp):
            self.dino.velocity_x = 2
            Clock.schedule_once(lambda dt: setattr(self.dino, 'velocity_x', 0), 5)
        elif isinstance(power_up, ShieldPowerUp):
            self.shield_active = True
            Clock.schedule_once(lambda dt: setattr(self, 'shield_active', False), 10)
        elif isinstance(power_up, AmmoPowerUp):
            self.shoot_cooldown = max(0.1, self.shoot_cooldown - 0.2)
        elif isinstance(power_up, HealthPowerUp):
            self.health = min(5, self.health + 1)
        elif isinstance(power_up, ScorePowerUp):
            self.score += 50
        self.remove_widget(power_up)
        self.stage.power_ups.remove(power_up)

    def update(self, dt: float) -> None:
        if not self.game_active or not self.dino:
            return

        # Update physics
        self.dino.velocity_y -= 0.10  # Gravity
        self.dino.move()
        self.invincibility_timer = max(0, self.invincibility_timer - dt)

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.move()
            if not (0 <= bullet.x <= self.width and 0 <= bullet.y <= self.height):
                self.remove_widget(bullet)
                self.bullets.remove(bullet)

        for bullet in self.boss_bullets[:]:
            bullet.move()
            if bullet.x < -bullet.width:
                self.remove_widget(bullet)
                self.boss_bullets.remove(bullet)
            elif self.dino.collide_widget(bullet) and self.invincibility_timer <= 0:
                self.handle_collision(bullet, is_boss_bullet=True)

        # Update obstacles and power-ups via Stage
        for obstacle in self.stage.obstacles[:]:
            for bullet in self.bullets[:]:
                if bullet.collide_widget(obstacle):
                    self.handle_bullet_hit(obstacle, bullet)
                    break
            if self.dino.collide_widget(obstacle) and self.invincibility_timer <= 0:
                self.handle_collision(obstacle)

        for power_up in self.stage.power_ups[:]:
            if self.dino.collide_widget(power_up):
                self.collect_power_up(power_up)

        # Check stage progression
        self.obstacles_cleared = self.stage.obstacles_cleared
        if self.obstacles_cleared >= self.obstacles_to_clear:
            self.next_stage()

    def handle_collision(self, widget, is_boss_bullet: bool = False) -> None:
        self.remove_widget(widget)
        if is_boss_bullet:
            self.boss_bullets.remove(widget)
        else:
            self.stage.obstacles.remove(widget)
            self.stage.obstacles_cleared += 1
            self.score += 1  # Minimal points for collision
         
        if self.shield_active:
            self.shield_active = False
        else:
            self.health -= 1
            self.invincibility_timer = 0.5
            if self.health <= 0:
                self.game_over()

    def handle_bullet_hit(self, obstacle, bullet) -> None:
        if isinstance(obstacle, Boss):
            obstacle.health -= 1
            if obstacle.health <= 0:
                self.stage.obstacles_cleared += 1
                self.score += 20
                self.remove_widget(obstacle)
                self.stage.obstacles.remove(obstacle)
        else:
            self.stage.obstacles_cleared += 1
            self.score += 5
            self.remove_widget(obstacle)
            self.stage.obstacles.remove(obstacle)
        self.remove_widget(bullet)
        self.bullets.remove(bullet)

    def next_stage(self):
        self.stage_number += 1
        self.stage.next_stage()  # Use Stage’s next_stage method
        if self.stage_number > 5:
            self.game_active = False

    def game_over(self) -> None:
        self.game_active = False
        for widget_list in (self.stage.obstacles, self.bullets, self.boss_bullets, self.stage.power_ups):
            for widget in widget_list[:]:
                self.remove_widget(widget)
            widget_list.clear()
        Clock.unschedule(self.update)

    def restart(self) -> None:
        self.game_over()
        self.game_active = True
        self.score = 0
        self.stage_number = 1
        self.obstacles_cleared = 0
        self.health = 3
        self.shield_active = False
        self.invincibility_timer = 0
        self.shoot_cooldown = 0.5
        self.last_shot_time = 0
        self.remove_widget(self.stage)
        self.stage = Stage(stage_number=self.stage_number)
        self.add_widget(self.stage)
        Clock.schedule_interval(self.update, 1.0 / 60.0)