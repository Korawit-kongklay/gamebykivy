from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from .player import Character
import random

class Enemy(Character):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    target = ObjectProperty(None)
    attack_range = NumericProperty(100)
    attack_cooldown = NumericProperty(1.0)
    move_speed = NumericProperty(3.0)
    vision_range = NumericProperty(200)
    facing_right = BooleanProperty(True)
    health = NumericProperty(100)
    max_health = NumericProperty(100)  # Added for HP bar scaling

    def __init__(self, gif_path: str = 'assets/gifs/turtle.gif', size: tuple = (80, 80), health=100, **kwargs):
        super().__init__(gif_path=gif_path, size=size, health=health, **kwargs)
        self.max_health = health  # Set max_health to initial health
        self.last_attack_time = 0
        self.wander_target = None
        self.wander_timer = 0
        self.wander_duration = random.uniform(2.0, 5.0)
        self.last_jump_time = 0
        self.next_jump_interval = random.uniform(2.0, 3.0)
        # Initialize hp_bar_instruction as None
        self.hp_bar_instruction = None
        # Call update_hp_bar after initialization
        self.update_hp_bar()
        Clock.schedule_interval(self.update_ai, 1.0 / 30.0)

    def move(self):
        new_pos = Vector(*self.velocity) + self.pos
        if new_pos[0] < 0:
            self.velocity_x = abs(self.velocity_x)
            self.facing_right = True
            new_pos[0] = 0
        elif new_pos[0] > Window.width - self.width:
            self.velocity_x = -abs(self.velocity_x)
            self.facing_right = False
            new_pos[0] = Window.width - self.width
        self.pos = new_pos
        if self.debug_hitbox_visible:
            self.update_hitbox_debug()
        self.update_hp_bar()  # Update HP bar position

    def update_ai(self, dt):
        if not self.target or not self.parent:
            # print("Enemy: No target or parent assigned.")
            return

        player_center_x = self.target.x + self.target.width / 2
        player_center_y = self.target.y + self.target.height / 2
        self_center_x = self.x + self.width / 2
        self_center_y = self.y + self.height / 2

        dx = player_center_x - self_center_x
        dy = player_center_y - self_center_y
        distance = Vector(dx, dy).length() or 0.001

        player_in_vision = distance <= self.vision_range and (
            (self.facing_right and dx > 0) or (not self.facing_right and dx < 0)
        )

        if player_in_vision:
            self.chase_player(dx, dy, distance)
        else:
            self.wander(dt)

        self.avoid_clumping()

        current_time = Clock.get_time()
        if distance <= self.attack_range and (current_time - self.last_attack_time >= self.attack_cooldown):
            self.attack()
            self.last_attack_time = current_time

        if self.velocity_x > 0:
            self.facing_right = True
        elif self.velocity_x < 0:
            self.facing_right = False

        # Uncomment for debugging
        # print(f"Enemy Pos: ({self.x:.2f}, {self.y:.2f}), Vel: ({self.velocity_x:.2f}, {self.velocity_y:.2f}), "
        #       f"Target Pos: ({self.target.x:.2f}, {self.target.y:.2f}), dx: {dx:.2f}, Distance: {distance:.2f}, "
        #       f"Facing Right: {self.facing_right}, In Vision: {player_in_vision}, Wander Target: {self.wander_target}, "
        #       f"Health: {self.health}")

    def chase_player(self, dx, dy, distance):
        if abs(dx) > 5:
            normalized_dx = dx / distance
            self.velocity_x = normalized_dx * self.move_speed
        else:
            self.velocity_x = 0

        current_time = Clock.get_time()
        if dy > 50 and abs(self.velocity_y) < 0.01 and (current_time - self.last_jump_time > 1.0):
            self.velocity_y = 5
            self.last_jump_time = current_time

    def wander(self, dt):
        self.wander_timer += dt

        if self.wander_target is None or self.wander_timer >= self.wander_duration:
            self.wander_target = (
                random.uniform(0, Window.width - self.width),
                random.uniform(0, Window.height - self.height)
            )
            self.wander_timer = 0
            self.wander_duration = random.uniform(2.0, 5.0)

        target_x, _ = self.wander_target
        self_center_x = self.x + self.width / 2
        dx = target_x - self_center_x
        distance = abs(dx) or 0.001

        if distance < 10:
            self.velocity_x = 0
        else:
            normalized_dx = dx / distance
            self.velocity_x = normalized_dx * self.move_speed * 0.7

        current_time = Clock.get_time()
        if (current_time - self.last_jump_time >= self.next_jump_interval) and abs(self.velocity_y) < 0.01:
            self.velocity_y = 5
            self.last_jump_time = current_time
            self.next_jump_interval = random.uniform(2.0, 3.0)

    def avoid_clumping(self):
        if not self.parent or not hasattr(self.parent, 'obstacles'):
            return
        for other in self.parent.obstacles:
            if other == self:
                continue
            dx = other.x - self.x
            dy = other.y - self.y
            distance = Vector(dx, dy).length() or 0.001
            if distance < self.width * 3:
                normalized_dx = dx / distance
                normalized_dy = dy / distance
                self.velocity_x -= normalized_dx * 2
                if abs(dy) < self.height * 2 and abs(self.velocity_y) < 0.01:
                    self.velocity_y = 5
                    self.last_jump_time = Clock.get_time()
                    self.next_jump_interval = random.uniform(2.0, 3.0)
                other.velocity_x += normalized_dx * 2

    def take_damage(self, damage):
        self.health -= damage
        self.update_hp_bar()  # Update HP bar when damaged
        if self.health <= 0:
            self.die()

    def die(self):
        if self.parent and self in self.parent.obstacles:
            self.parent.obstacles.remove(self)
            self.parent.remove_widget(self)
            print(f"Enemy at {self.pos} has died.")

    def attack(self):
        from .attack import EnemyProjectile
        if not self.parent or not isinstance(self.parent, Widget):
            return
        game = self.parent.parent if self.parent.parent else None
        if game and hasattr(game, 'enemy_attacks'):
            attack = EnemyProjectile(start_pos=(self.x + self.width / 2, self.y + self.height / 2),
                                    target_pos=(self.target.x + self.target.width / 2, self.target.y + self.target.height / 2))
            game.add_widget(attack)
            game.enemy_attacks.append(attack)

    def update_hp_bar(self):
        """Draw or update the HP bar above the enemy."""
        # Ensure hp_bar_instruction exists before removing it
        if hasattr(self, 'hp_bar_instruction') and self.hp_bar_instruction:
            self.canvas.after.remove(self.hp_bar_instruction)
        hp_width = (self.health / self.max_health) * self.width  # Scale bar width
        with self.canvas.after:
            Color(1, 0, 0, 1)  # Red for enemy
            self.hp_bar_instruction = Rectangle(
                pos=(self.x, self.y + self.height + 5),  # 5 pixels above
                size=(hp_width, 5)  # 5 pixels high
            )