from .enemy import Enemy
from .hitbox import Hitbox
from kivy.properties import NumericProperty
import random
import math
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse

class Boss(Enemy):
    health = NumericProperty(5)  # เพิ่ม HP เป็น 5 เพื่อให้ต่อสู้นานขึ้น
    attack_cooldown = NumericProperty(1.0)  # ลดจาก 2.0 เป็น 1.0 วินาที
    is_enraged = False  # Track enrage mode

    def __init__(self, **kwargs):
        super().__init__(gif_path='assets/gifs/jacko.gif', size=(60, 80), velocity_x=-1, **kwargs)
        self.hitbox = Hitbox(offset_x=0, offset_y=0, width=60, height=80)  # Set hitbox for boss
        self.last_attack_time = 0
        self.last_summon_time = 0
        self.last_dash_time = 0
        self.last_aoe_time = 0
        self.last_teleport_time = 0
        self.last_ground_slam_time = 0
        self.dash_cooldown = 3.0  # ลดจาก 5.0 เป็น 3.0 วินาที
        self.summon_cooldown = 5.0  # ลดจาก 10.0 เป็น 5.0 วินาที
        self.aoe_cooldown = 4.0  # AoE ทุก 4 วินาที
        self.teleport_cooldown = 6.0  # Teleport ทุก 6 วินาที
        self.ground_slam_cooldown = 5.0  # Ground Slam ทุก 5 วินาที
        self.enrage_threshold = 2  # เข้า Enrage Mode เมื่อ HP เหลือ 2
        self.aoe_warning = None  # Widget สำหรับแสดงวงเตือน AoE

    def get_hitbox_rect(self):
        """Return the hitbox rectangle for collision detection."""
        return self.hitbox.get_rect(self.x, self.y)

    def update(self, game, dt):
        """Update boss behavior and handle attacks."""
        current_time = Clock.get_time()

        # Check for enrage mode
        if self.health <= self.enrage_threshold and not self.is_enraged:
            self.enter_enrage_mode()

        # Dash attack
        if current_time - self.last_dash_time >= self.dash_cooldown:
            self.dash_attack(game)
            self.last_dash_time = current_time

        # Summon minions
        if current_time - self.last_summon_time >= self.summon_cooldown:
            self.summon_minions(game)
            self.last_summon_time = current_time

        # Enhanced shoot
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.enhanced_shoot(game)
            self.last_attack_time = current_time

        # AoE attack
        if current_time - self.last_aoe_time >= self.aoe_cooldown:
            self.aoe_attack(game)
            self.last_aoe_time = current_time

        # Teleport
        if current_time - self.last_teleport_time >= self.teleport_cooldown:
            self.teleport(game)
            self.last_teleport_time = current_time

        # Ground Slam
        if current_time - self.last_ground_slam_time >= self.ground_slam_cooldown:
            self.ground_slam(game)
            self.last_ground_slam_time = current_time

    def dash_attack(self, game):
        """Perform a dash attack towards the current direction, damaging player on collision."""
        print("Boss is dashing!")
        dash_speed = self.velocity_x * 3  # Triple the speed
        self.velocity_x = dash_speed
        Clock.schedule_once(self.reset_dash, 0.5)

        # Check for collision with player during dash
        player_rect = game.player.get_hitbox_rect()
        boss_rect = self.get_hitbox_rect()
        if Hitbox.collide(boss_rect, player_rect):
            game.player.take_damage(2)  # Deal 2 damage on dash collision
            print("Boss dashed into player, dealing 2 damage!")

    def reset_dash(self, dt):
        """Reset speed after dash."""
        self.velocity_x = -1 if not self.is_enraged else -2  # Reset to normal or enraged speed

    def summon_minions(self, game):
        """Summon smaller enemies to assist the boss."""
        print("Boss is summoning minions!")
        minion_count = 2
        for _ in range(minion_count):
            spawn_x = random.uniform(self.x - 100, self.x + 100)
            spawn_y = random.uniform(0, Window.height - 80)
            # Ensure spawn position is within bounds
            spawn_x = max(0, min(spawn_x, Window.width - 80))
            spawn_y = max(0, min(spawn_y, Window.height - 80))
            minion = Enemy(pos=(spawn_x, spawn_y))
            game.stage.add_widget(minion)
            game.stage.obstacles.append(minion)
            minion.target = game.player

    def enhanced_shoot(self, game):
        """Shoot multiple projectiles in a spread pattern towards the player."""
        print("Boss is using enhanced shoot!")
        from .attack import EnemyProjectile
        # Calculate direction towards player
        target_pos = (game.player.x, game.player.y)
        start_pos = (self.x - 15, self.y + self.height / 2)
        # Shoot 3 projectiles in a spread
        angles = [-30, 0, 30]  # Angles for spread
        for angle in angles:
            # Adjust target position based on angle
            dx, dy = target_pos[0] - start_pos[0], target_pos[1] - start_pos[1]
            distance = max((dx**2 + dy**2)**0.5, 0.1)
            base_angle = math.degrees(math.atan2(dy, dx))
            adjusted_angle = base_angle + angle
            # Create projectile
            attack = EnemyProjectile(start_pos=start_pos, target_pos=(
                start_pos[0] + distance * math.cos(math.radians(adjusted_angle)),
                start_pos[1] + distance * math.sin(math.radians(adjusted_angle))
            ))
            game.add_widget(attack)
            game.enemy_attacks.append(attack)

    def aoe_attack(self, game):
        """Perform an Area of Effect attack around the boss."""
        print("Boss is preparing AoE attack!")
        # Show warning circle
        if self.aoe_warning:
            self.remove_widget(self.aoe_warning)
        self.aoe_warning = Widget(pos=(self.x - 90, self.y - 90), size=(200, 200))
        with self.aoe_warning.canvas:
            Color(1, 0, 0, 0.5)  # Red semi-transparent warning
            self.aoe_warning.circle = Ellipse(pos=self.aoe_warning.pos, size=self.aoe_warning.size)
        game.add_widget(self.aoe_warning)
        # Schedule the actual AoE damage after 1 second
        Clock.schedule_once(lambda dt: self.execute_aoe(game), 1.0)

    def execute_aoe(self, game):
        """Execute the AoE attack, dealing damage to the player if within range."""
        print("Boss executes AoE attack!")
        if self.aoe_warning:
            game.remove_widget(self.aoe_warning)
            self.aoe_warning = None
        # Check if player is within AoE range (200x200 area centered on boss)
        aoe_rect = {'x': self.x - 90, 'y': self.y - 90, 'width': 200, 'height': 200,
                    'right': self.x + 110, 'top': self.y + 110}
        player_rect = game.player.get_hitbox_rect()
        if Hitbox.collide(aoe_rect, player_rect):
            game.player.take_damage(3)  # Deal 3 damage if player is in range
            print("Player hit by AoE attack, dealing 3 damage!")

    def teleport(self, game):
        """Teleport to a random position on the screen."""
        print("Boss is teleporting!")
        new_x = random.uniform(0, Window.width - self.width)
        new_y = random.uniform(0, Window.height - self.height)
        self.pos = (new_x, new_y)

    def ground_slam(self, game):
        """Perform a ground slam, jumping up and slamming down to deal damage."""
        print("Boss is performing Ground Slam!")
        # Jump up
        self.velocity_y = 8  # Jump velocity
        # Schedule the slam after 0.5 seconds (during the jump)
        Clock.schedule_once(lambda dt: self.execute_ground_slam(game), 0.5)

    def execute_ground_slam(self, game):
        """Execute the ground slam, dealing damage if player is nearby."""
        print("Boss slams the ground!")
        self.velocity_y = -10  # Slam down
        # Check if player is within range (150x150 area centered on boss)
        slam_rect = {'x': self.x - 45, 'y': self.y - 45, 'width': 150, 'height': 150,
                     'right': self.x + 105, 'top': self.y + 105}
        player_rect = game.player.get_hitbox_rect()
        if Hitbox.collide(slam_rect, player_rect):
            game.player.take_damage(2)  # Deal 2 damage if player is in range
            print("Player hit by Ground Slam, dealing 2 damage!")

    def enter_enrage_mode(self):
        """Enter enrage mode when health is low, adding an immediate AoE attack."""
        print("Boss has entered enrage mode!")
        self.is_enraged = True
        self.velocity_x *= 2  # Double movement speed
        self.attack_cooldown *= 0.5  # Halve attack cooldown
        self.dash_cooldown *= 0.5  # Halve dash cooldown
        self.summon_cooldown *= 0.5  # Halve summon cooldown
        self.aoe_cooldown *= 0.5  # Halve AoE cooldown
        self.teleport_cooldown *= 0.5  # Halve teleport cooldown
        self.ground_slam_cooldown *= 0.5  # Halve ground slam cooldown
        # Perform an immediate AoE attack upon entering enrage mode
        self.aoe_attack(self.parent)

    def shoot(self, game):
        """Default shoot method, kept for compatibility."""
        self.enhanced_shoot(game)  # Redirect to enhanced_shoot