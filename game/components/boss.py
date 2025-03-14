from .enemy import Enemy
from .hitbox import Hitbox
from kivy.properties import NumericProperty, ReferenceListProperty, BooleanProperty
from kivy.vector import Vector
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
import random
import math

class Boss(Enemy):
    health = NumericProperty(5)  # Increased HP for longer fights
    attack_cooldown = NumericProperty(1.0)  # Cooldown for enhanced shoot
    velocity_x = NumericProperty(0)  # Start stationary
    velocity_y = NumericProperty(0)  # From Enemy
    velocity = ReferenceListProperty(velocity_x, velocity_y)  # From Enemy
    move_speed = NumericProperty(3.0)  # Speed for chasing/wandering
    vision_range = NumericProperty(0)  # Effectively infinite
    attack_range = NumericProperty(150)  # Range for triggering attacks
    facing_right = BooleanProperty(True)  # Track direction like Enemy
    is_enraged = False  # Track enrage mode

    def __init__(self, **kwargs):
        # Original size (80, 80) multiplied by 3 = (240, 240)
        super().__init__(gif_path='assets/gifs/boss.gif', size=(240, 240), velocity_x=0, **kwargs)
        # Scale hitbox proportionally: original (60, 80) * 3 = (180, 240)
        self.hitbox = Hitbox(offset_x=30, offset_y=0, width=180, height=240)  # Adjusted for new size
        self.target = None  # Will be set to player by game logic
        # Timers for attacks
        self.last_attack_time = 0
        self.last_summon_time = 0
        self.last_dash_time = 0
        self.last_aoe_time = 0
        self.last_teleport_time = 0
        self.last_ground_slam_time = 0
        # Cooldowns for attacks
        self.dash_cooldown = 3.0
        self.summon_cooldown = 5.0
        self.aoe_cooldown = 4.0
        self.teleport_cooldown = 6.0
        self.ground_slam_cooldown = 5.0
        self.enrage_threshold = 2  # Enter enrage mode at HP <= 2
        self.aoe_warning = None  # Widget for AoE warning
        # AI-specific attributes from Enemy, adjusted for longer idling
        self.wander_target = None
        self.wander_timer = 0
        self.wander_duration = random.uniform(5.0, 10.0)  # Increased range for longer idling
        self.last_jump_time = 0
        self.next_jump_interval = random.uniform(2.0, 3.0)

    def update_ai(self, dt):
        """Override to prevent Enemy's update_ai from running."""
        pass  # Do nothing; Boss uses its own update method

    def move(self):
        """Move the boss like Enemy, respecting boundaries."""
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
        self.update_hp_bar()

    def update(self, game, dt):
        """AI logic with infinite vision and boss attacks."""
        if not self.target or not game:
            print("Boss: No target or game assigned.")
            return

        current_time = Clock.get_time()
        player_center_x = self.target.x + self.target.width / 2
        player_center_y = self.target.y + self.target.height / 2
        self_center_x = self.x + self.width / 2
        self_center_y = self.y + self.height / 2

        dx = player_center_x - self_center_x
        dy = player_center_y - self_center_y
        distance = Vector(dx, dy).length() or 0.001

        # Infinite vision: Player is always in vision
        player_in_vision = True

        # Check for enrage mode
        if self.health <= self.enrage_threshold and not self.is_enraged:
            self.enter_enrage_mode(game)

        # Movement behavior
        if player_in_vision:
            self.chase_player(dx, dy, distance)
        else:
            self.wander(dt)  # Won't trigger due to infinite vision

        self.avoid_clumping(game)

        # Update facing direction
        if self.velocity_x > 0:
            self.facing_right = True
        elif self.velocity_x < 0:
            self.facing_right = False

        # Boss-specific attacks
        self.update_attacks(game, current_time, distance)

    def chase_player(self, dx, dy, distance):
        """Chase the player like Enemy."""
        if abs(dx) > 5:
            normalized_dx = dx / distance
            self.velocity_x = normalized_dx * self.move_speed
        else:
            self.velocity_x = 0

        if dy > 50 and abs(self.velocity_y) < 0.01 and (Clock.get_time() - self.last_jump_time > 1.0):
            self.velocity_y = 5
            self.last_jump_time = Clock.get_time()

    def wander(self, dt):
        """Wander randomly when player is out of vision (not used with infinite vision)."""
        self.wander_timer += dt
        if self.wander_target is None or self.wander_timer >= self.wander_duration:
            self.wander_target = (
                random.uniform(0, Window.width - self.width),
                random.uniform(0, Window.height - self.height)
            )
            self.wander_timer = 0
            self.wander_duration = random.uniform(5.0, 10.0)

        target_x, _ = self.wander_target
        self_center_x = self.x + self.width / 2
        dx = target_x - self_center_x
        distance = abs(dx) or 0.001

        if distance < 10:
            self.velocity_x = 0
        else:
            normalized_dx = dx / distance
            self.velocity_x = normalized_dx * self.move_speed * 0.7

        if (Clock.get_time() - self.last_jump_time >= self.next_jump_interval) and abs(self.velocity_y) < 0.01:
            self.velocity_y = 5
            self.last_jump_time = Clock.get_time()
            self.next_jump_interval = random.uniform(2.0, 3.0)

    def avoid_clumping(self, game):
        """Avoid clumping with other obstacles, like Enemy."""
        if not game or not hasattr(game, 'obstacles'):
            return
        for other in game.obstacles:
            if other == self:
                continue
            dx = other.x - self.x
            dy = other.y - self.y
            distance = Vector(dx, dy).length() or 0.001
            if distance < self.width * 3:  # Scaled with size increase
                normalized_dx = dx / distance
                self.velocity_x -= normalized_dx * 2
                if abs(dy) < self.height * 2 and abs(self.velocity_y) < 0.01:
                    self.velocity_y = 5
                    self.last_jump_time = Clock.get_time()
                    self.next_jump_interval = random.uniform(2.0, 3.0)
                other.velocity_x += normalized_dx * 2

    def update_attacks(self, game, current_time, distance):
        """Handle boss-specific attacks with emphasis on shooting."""
        # Enhanced shoot (prioritized with infinite vision)
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.enhanced_shoot(game)
            self.last_attack_time = current_time

        # Other attacks remain available but are secondary
        if current_time - self.last_dash_time >= self.dash_cooldown and distance <= self.attack_range:
            self.dash_attack(game)
            self.last_dash_time = current_time

        if current_time - self.last_summon_time >= self.summon_cooldown:
            self.summon_minions(game)
            self.last_summon_time = current_time

        if current_time - self.last_aoe_time >= self.aoe_cooldown:
            self.aoe_attack(game)
            self.last_aoe_time = current_time

        if current_time - self.last_teleport_time >= self.teleport_cooldown:
            self.teleport(game)
            self.last_teleport_time = current_time

        if current_time - self.last_ground_slam_time >= self.ground_slam_cooldown and distance <= self.attack_range:
            self.ground_slam(game)
            self.last_ground_slam_time = current_time

    def dash_attack(self, game):
        """Perform a dash attack."""
        print("Boss is dashing!")
        dash_speed = self.velocity_x * 3 if self.velocity_x != 0 else (3 if self.facing_right else -3)
        self.velocity_x = dash_speed
        Clock.schedule_once(self.reset_dash, 0.5)
        player_rect = game.player.get_hitbox_rect()
        boss_rect = self.get_hitbox_rect()
        if Hitbox.collide(boss_rect, player_rect):
            game.player.take_damage(2)
            print("Boss dashed into player, dealing 2 damage!")

    def reset_dash(self, dt):
        """Reset speed after dash."""
        self.velocity_x = 0

    def summon_minions(self, game):
        """Summon smaller enemies."""
        print("Boss is summoning minions!")
        minion_count = 2
        for _ in range(minion_count):
            spawn_x = random.uniform(self.x - 100, self.x + 100)
            spawn_y = random.uniform(0, Window.height - 80)
            spawn_x = max(0, min(spawn_x, Window.width - 80))
            spawn_y = max(0, min(spawn_y, Window.height - 80))
            minion = Enemy(pos=(spawn_x, spawn_y))
            game.stage.add_widget(minion)
            game.stage.obstacles.append(minion)
            minion.target = game.player

    def enhanced_shoot(self, game):
        """Shoot multiple projectiles in a spread pattern toward the player."""
        print("Boss is using enhanced shoot!")
        from .attack import EnemyProjectile
        target_pos = (game.player.x, game.player.y)
        start_pos = (self.x + self.width / 2, self.y + self.height / 2)  # Center of boss
        angles = [-30, 0, 30]
        for angle in angles:
            dx, dy = target_pos[0] - start_pos[0], target_pos[1] - start_pos[1]
            distance = max((dx**2 + dy**2)**0.5, 0.1)
            base_angle = math.degrees(math.atan2(dy, dx))
            adjusted_angle = base_angle + angle
            attack = EnemyProjectile(start_pos=start_pos, target_pos=(
                start_pos[0] + distance * math.cos(math.radians(adjusted_angle)),
                start_pos[1] + distance * math.sin(math.radians(adjusted_angle))
            ))
            game.add_widget(attack)
            game.enemy_attacks.append(attack)

    def aoe_attack(self, game):
        """Perform an AoE attack."""
        print("Boss is preparing AoE attack!")
        if self.aoe_warning:
            self.remove_widget(self.aoe_warning)
        # Scale AoE warning with size: original (200, 200) * 3 = (600, 600)
        self.aoe_warning = Widget(pos=(self.x - 270, self.y - 270), size=(600, 600))
        with self.aoe_warning.canvas:
            Color(1, 0, 0, 0.5)
            self.aoe_warning.circle = Ellipse(pos=self.aoe_warning.pos, size=self.aoe_warning.size)
        game.add_widget(self.aoe_warning)
        Clock.schedule_once(lambda dt: self.execute_aoe(game), 1.0)

    def execute_aoe(self, game):
        """Execute the AoE attack."""
        print("Boss executes AoE attack!")
        if self.aoe_warning:
            game.remove_widget(self.aoe_warning)
            self.aoe_warning = None
        # Scale AoE rect: original (200, 200) * 3 = (600, 600)
        aoe_rect = {'x': self.x - 270, 'y': self.y - 270, 'width': 600, 'height': 600,
                    'right': self.x + 330, 'top': self.y + 330}
        player_rect = game.player.get_hitbox_rect()
        if Hitbox.collide(aoe_rect, player_rect):
            game.player.take_damage(3)
            print("Player hit by AoE attack, dealing 3 damage!")

    def teleport(self, game):
        """Teleport to a random position."""
        print("Boss is teleporting!")
        new_x = random.uniform(0, Window.width - self.width)
        new_y = random.uniform(0, Window.height - self.height)
        self.pos = (new_x, new_y)

    def ground_slam(self, game):
        """Perform a ground slam."""
        print("Boss is performing Ground Slam!")
        self.velocity_y = 8
        Clock.schedule_once(lambda dt: self.execute_ground_slam(game), 0.5)

    def execute_ground_slam(self, game):
        """Execute the ground slam."""
        print("Boss slams the ground!")
        self.velocity_y = -10
        # Scale slam rect: original (150, 150) * 3 = (450, 450)
        slam_rect = {'x': self.x - 135, 'y': self.y - 135, 'width': 450, 'height': 450,
                     'right': self.x + 315, 'top': self.y + 315}
        player_rect = game.player.get_hitbox_rect()
        if Hitbox.collide(slam_rect, player_rect):
            game.player.take_damage(2)
            print("Player hit by Ground Slam, dealing 2 damage!")

    def enter_enrage_mode(self, game):
        """Enter enrage mode when health is low."""
        print("Boss has entered enrage mode!")
        self.is_enraged = True
        self.move_speed *= 2  # Double movement speed
        self.attack_cooldown *= 0.5
        self.dash_cooldown *= 0.5
        self.summon_cooldown *= 0.5
        self.aoe_cooldown *= 0.5
        self.teleport_cooldown *= 0.5
        self.ground_slam_cooldown *= 0.5
        self.aoe_attack(game)

    def shoot(self, game):
        """Default shoot method."""
        self.enhanced_shoot(game)