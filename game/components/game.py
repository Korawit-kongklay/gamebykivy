from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from .player import Player
from .stage import Stage
from .hitbox import Hitbox
from .boss import Boss
from .enemy import Enemy
from .attack import ProjectileAttack
from .portal import Portal
import random  # For random positioning

class Game(Widget):
    """Main game widget managing game state, entities, and interactions."""
    portal = ObjectProperty(None, allownone=True)  # ประกาศครั้งเดียว
    player = ObjectProperty(None)
    stage = ObjectProperty(None)
    boss = ObjectProperty(None)
    score = NumericProperty(0)
    stage_number = NumericProperty(1)
    player_health = NumericProperty(20)  # Player starts with 20 HP (10 hearts)
    player_max_health = NumericProperty(20)  # Max health is 20
    game_active = BooleanProperty(True)
    player_attacks = ListProperty([])
    enemy_attacks = ListProperty([])
    debug_hitbox = BooleanProperty(False)

    ENABLE_PLAYER = True
    ENABLE_ENEMIES = True
    ENABLE_ATTACKS = True
    ENABLE_BOSS = False
    MAX_STAGES = 5  # Maximum number of stages

    def __init__(self, initial_player_hp=20, **kwargs):
        super().__init__(**kwargs)
        self.initial_player_hp = initial_player_hp
        self.hp_layout = None  # Will hold the BoxLayout for hearts
        self.initialize_game()
        self.bind_inputs()
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        if self.ENABLE_BOSS:
            Clock.schedule_interval(self.spawn_boss_check, 5)
        # Schedule an initial update after the widget is added to the window
        Clock.schedule_once(self._initial_update, 0)

    def _initial_update(self, dt):
        """Ensure hearts are drawn at the correct position after initialization."""
        self.update_hp_hearts()

    def initialize_game(self):
        """Initialize the game state and entities."""
        self.stage = Stage(stage_number=self.stage_number, spawn_obstacles=self.ENABLE_ENEMIES)
        self.add_widget(self.stage)
        if self.ENABLE_ENEMIES:
            self.spawn_initial_enemies()
        if self.ENABLE_PLAYER:
            self.player = Player(pos=(100, 0), health=self.initial_player_hp)
            self.player_health = self.player.health
            self.player_max_health = self.player.max_health
            self.add_widget(self.player)
            self.player.bind(health=self.on_player_health_changed)
            for enemy in self.stage.obstacles:
                enemy.target = self.player
                # print(f"Set target for enemy at {enemy.pos} to player at {self.player.pos}")
        self.attack_cooldown = 0.5
        self.last_attack_time = 0
        self.boss_attack_cooldown = 2.0
        self.last_boss_attack = 0
        self.mouse_pos = (0, 0)
        self.score = 0
        self.on_platform = False
        # ไม่เรียก self.spawn_portal() ที่นี่
        # Initialize hp_layout
        self.hp_layout = self.ids.hp_layout  # Access BoxLayout via id
        self.hp_layout.bind(pos=self._update_hp_position)  # Bind pos to update hearts
        self.update_hp_hearts()  # Set up initial heart display

    def spawn_initial_enemies(self):
        """Spawn initial enemies at random positions based on stage number."""
        enemy_count = 5 + (self.stage_number - 1)  # Stage 1: 5, Stage 2: 6, etc.
        self.stage.obstacles.clear()  # Clear existing obstacles
        enemy_size = (80, 80)  # Assuming Enemy size from your previous code; adjust if different
        for _ in range(enemy_count):
            # Random x and y within window bounds, accounting for enemy size
            spawn_x = random.uniform(0, Window.width - enemy_size[0])
            spawn_y = random.uniform(0, Window.height - enemy_size[1])
            enemy = Enemy(pos=(spawn_x, spawn_y))
            self.stage.add_widget(enemy)
            self.stage.obstacles.append(enemy)

    def spawn_portal(self):
        """Spawn or reposition the portal."""
        if self.portal:
            self.remove_widget(self.portal)
        portal_x = Window.width - 60
        portal_y = 10
        self.portal = Portal(pos=(portal_x, portal_y))
        self.add_widget(self.portal)
        print(f"Portal spawned at {self.portal.pos}")

    def _update_hp_position(self, instance, value):
        """Update heart positions when hp_layout moves."""
        self.update_hp_hearts()

    def bind_inputs(self):
        self.keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self.keyboard.bind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        Window.bind(mouse_pos=self._on_mouse_pos)
        if self.ENABLE_ATTACKS:
            Window.bind(on_mouse_down=self._on_mouse_down)

    def _keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        self.keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if not self.game_active:
            return False
        if keycode[1] == 'h':
            self.debug_hitbox = not self.debug_hitbox
            self.update_hitbox_visibility()
            return True
        if not self.ENABLE_PLAYER or not self.player:
            return False
        if keycode[1] == 'spacebar':
            if self.can_jump(self.player):
                self.player.velocity_y = 6
        elif keycode[1] in ('left', 'a'):
            self.player.velocity_x = -5
        elif keycode[1] in ('right', 'd'):
            self.player.velocity_x = 5
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        if self.ENABLE_PLAYER and self.player and keycode[1] in ('left', 'a', 'right', 'd'):
            self.player.velocity_x = 0
        return True

    def _on_mouse_pos(self, window, pos):
        self.mouse_pos = pos

    def _on_mouse_down(self, window, x, y, button, modifiers):
        if button != 'left' or not self.game_active or (Clock.get_time() - self.last_attack_time < self.attack_cooldown):
            return
        start_pos = (self.player.x + self.player.width, self.player.y + self.player.height / 2)
        attack = ProjectileAttack(start_pos=start_pos, target_pos=self.mouse_pos, speed=15)
        self.add_widget(attack)
        self.player_attacks.append(attack)
        self.last_attack_time = Clock.get_time()

    def spawn_boss_check(self, dt):
        if not self.ENABLE_BOSS or not self.game_active:
            return
        if not self.boss and self.score >= 10:
            self.boss = Boss(pos=(Window.width - 60, 0))
            self.add_widget(self.boss)
            self.boss.velocity_x = -1

    def on_player_health_changed(self, instance, value):
        """Callback to update UI when player health changes."""
        self.player_health = value
        self.update_hp_hearts()  # Update heart display

    def update_hp_hearts(self):
        """Update the heart display using Image widgets in the hp_layout."""
        if not self.hp_layout:
            return

        # Clear previous heart widgets
        self.hp_layout.clear_widgets()

        max_hearts = int(self.player_max_health / 2)  # Total heart slots (10 for 20 HP)
        full_hearts = int(self.player_health / 2)  # Number of full hearts (2 HP each)
        half_heart = self.player_health % 2 == 1  # True if there’s 1 HP left

        # Add full hearts
        for _ in range(full_hearts):
            heart = Image(
                source='assets/images/full_heart.png',
                size=(50, 50),
                allow_stretch=True,
                keep_ratio=False
            )
            self.hp_layout.add_widget(heart)

        # Add half heart if applicable
        if half_heart:
            half = Image(
                source='assets/images/half_heart.png',
                size=(50, 50),
                allow_stretch=True,
                keep_ratio=False
            )
            self.hp_layout.add_widget(half)

        # Add blank hearts for remaining slots up to max_hearts
        remaining_hearts = max_hearts - full_hearts - (1 if half_heart else 0)
        for _ in range(remaining_hearts):
            blank = Image(
                source='assets/images/blank_heart.png',
                size=(50, 50),
                allow_stretch=True,
                keep_ratio=False
            )
            self.hp_layout.add_widget(blank)

    def update(self, dt):
        if not self.game_active:
            return

        if self.ENABLE_PLAYER and self.player:
            self.apply_gravity(self.player)
            self.player.move()
            self.on_platform = self.handle_platform_collision(self.player)
            self.player_health = self.player.health  # Sync with Player's health
            # print(f"Player Position - x: {self.player.x:.2f}, y: {self.player.y:.2f}, on_platform: {self.on_platform}, HP: {self.player.health}")
            if self.debug_hitbox:
                self.player.update_hitbox_debug()
        
        if self.ENABLE_ENEMIES and len(self.stage.obstacles) == 0 and not self.boss and not self.portal:
            self.spawn_portal()
            print(f"Portal spawned after clearing Stage {self.stage_number}")

        if self.boss:
            self.apply_gravity(self.boss)
            self.boss.move()
            self.handle_platform_collision(self.boss)
            if self.boss.x < 0:
                self.boss.x = 0
            current_time = Clock.get_time()
            if current_time - self.last_boss_attack >= self.boss_attack_cooldown:
                self.boss.shoot(self)
                self.last_boss_attack = current_time
            if self.debug_hitbox:
                self.boss.update_hitbox_debug()

        if self.ENABLE_ATTACKS:
            self.update_attacks()

        if self.ENABLE_ENEMIES:
            self.update_enemies()

        # Check collision with portal and advance to next stage
        if self.portal and self.player and Hitbox.collide(self.player.get_hitbox_rect(), self.portal.get_hitbox_rect()):
            self.next_stage()

        # เรียก spawn_portal เมื่อเคลียร์ด่าน (Stage 1: ศัตรูหมด)
        if self.stage_number == 1 and self.ENABLE_ENEMIES and len(self.stage.obstacles) == 0 and not self.boss and not self.portal:
            self.spawn_portal()
            print("Portal spawned after clearing Stage 1")

        # Check for game completion (last stage, no enemies or boss)
        if self.stage_number == self.MAX_STAGES and not self.stage.obstacles and not self.boss:
            self.game_active = False
            print("Game Completed! All stages cleared!")

        if self.player_health <= 0:
            self.game_active = False
            print("Game Over!")

    def next_stage(self):
        """Advance to the next stage."""
        if self.stage_number >= self.MAX_STAGES:
            return  # Stop if at max stage
        self.stage_number += 1
        print(f"Moving to Stage {self.stage_number}")
        for attack in self.player_attacks + self.enemy_attacks:
            self.remove_widget(attack)
        self.player_attacks.clear()
        self.enemy_attacks.clear()
        if self.portal:
            self.remove_widget(self.portal)
            self.portal = None
        self.remove_widget(self.stage)
        self.stage = Stage(stage_number=self.stage_number, spawn_obstacles=self.ENABLE_ENEMIES)
        self.add_widget(self.stage)
        if self.ENABLE_ENEMIES:
            self.spawn_initial_enemies()
            for enemy in self.stage.obstacles:
                enemy.target = self.player
                # print(f"Stage {self.stage_number}: Set target for enemy at {enemy.pos} to player at {self.player.pos}")
            self.stage.spawn_obstacles()
            for enemy in self.stage.obstacles:
                enemy.target = self.player
                # print(f"Stage {self.stage_number}: Set target for enemy at {enemy.pos} to player at {self.player.pos}")
        if self.ENABLE_PLAYER:
            self.player.pos = (100, 0)
            self.player.velocity_x = 0
            self.player.velocity_y = 0
        # ไม่เรียก self.spawn_portal() ที่นี่ แต่ให้จัดการใน update
        self.update_hp_hearts()  # Reset hearts on stage change

    def update_hitbox_visibility(self):
        if self.player:
            self.player.toggle_hitbox_debug(self.debug_hitbox)
        for platform in self.stage.platforms:
            platform.toggle_hitbox_debug(self.debug_hitbox)
        if self.boss:
            self.boss.toggle_hitbox_debug(self.debug_hitbox)
        for enemy in self.stage.obstacles:
            enemy.toggle_hitbox_debug(self.debug_hitbox)

    def apply_gravity(self, entity):
        entity.velocity_y -= 0.15

    def can_jump(self, entity):
        on_ground = entity.y <= 0
        on_platform = self.is_on_platform(entity)
        return (on_ground or on_platform) and abs(entity.velocity_y) < 0.01

    def is_on_platform(self, entity):
        entity_rect = entity.get_hitbox_rect()
        for platform in self.stage.platforms:
            plat_rect = platform.get_hitbox_rect()
            if Hitbox.collide(entity_rect, plat_rect) and entity.velocity_y <= 0:
                distance = plat_rect['top'] - entity_rect['y']
                if -5 <= distance <= 10:
                    return True
        return False

    def handle_platform_collision(self, entity):
        entity_rect = entity.get_hitbox_rect()
        on_platform = False
        entity_prev_y = entity.y + entity.velocity_y

        for platform in self.stage.platforms:
            plat_rect = platform.get_hitbox_rect()
            if Hitbox.collide(entity_rect, plat_rect):
                if entity.velocity_y <= 0 and entity_prev_y + entity_rect['height'] > plat_rect['top']:
                    distance = plat_rect['top'] - entity_rect['y']
                    if -5 <= distance <= 10:
                        entity.y = plat_rect['top'] - entity.hitbox.offset_y
                        entity.velocity_y = 0
                        on_platform = True
                        continue
                continue

        if entity.y <= 0:
            entity.y = 0
            entity.velocity_y = 0
            on_platform = True

        return on_platform

    def update_attacks(self):
        for attack in self.player_attacks[:]:
            attack.move()
            if not (0 <= attack.x <= Window.width and 0 <= attack.y <= Window.height):
                self.remove_widget(attack)
                self.player_attacks.remove(attack)
            else:
                attack_rect = attack.get_hitbox_rect()
                if self.boss and Hitbox.collide(attack_rect, self.boss.get_hitbox_rect()):
                    self.boss.health -= 1
                    self.remove_widget(attack)
                    self.player_attacks.remove(attack)
                    if self.boss.health <= 0:
                        self.remove_widget(self.boss)
                        self.boss = None
                        self.score += 50
                elif self.ENABLE_ENEMIES:
                    for enemy in self.stage.obstacles[:]:
                        enemy_rect = enemy.get_hitbox_rect()
                        if Hitbox.collide(attack_rect, enemy_rect):
                            enemy.take_damage(100)
                            self.remove_widget(attack)
                            self.player_attacks.remove(attack)
                            if enemy.health <= 0:
                                self.score += 100
                                print(f"Enemy killed! Score increased to {self.score}")
                            break

        for attack in self.enemy_attacks[:]:
            attack.move()
            if not (0 <= attack.x <= Window.width and 0 <= attack.y <= Window.height):
                self.remove_widget(attack)
                self.enemy_attacks.remove(attack)
            elif Hitbox.collide(attack.get_hitbox_rect(), self.player.get_hitbox_rect()):
                self.player.take_damage(1)
                self.remove_widget(attack)
                self.enemy_attacks.remove(attack)

    def update_enemies(self):
        for enemy in self.stage.obstacles[:]:
            self.apply_gravity(enemy)
            enemy.move()
            self.handle_platform_collision(enemy)
            if Hitbox.collide(self.player.get_hitbox_rect(), enemy.get_hitbox_rect()):
                self.player.take_damage(1)
                self.stage.remove_widget(enemy)
                self.stage.obstacles.remove(enemy)
            elif enemy.x < -enemy.width:
                self.stage.remove_widget(enemy)
                self.stage.obstacles.remove(enemy)
            if self.debug_hitbox:
                enemy.update_hitbox_debug()

    def restart(self):
        self.game_active = True
        self.score = 0
        self.stage_number = 1
        self.player_health = self.initial_player_hp
        self.player_max_health = self.initial_player_hp
        self.player_attacks.clear()
        self.enemy_attacks.clear()
        if self.boss:
            self.remove_widget(self.boss)
            self.boss = None
        if self.portal:
            self.remove_widget(self.portal)
            self.portal = None
        self.remove_widget(self.stage)
        self.stage = Stage(stage_number=self.stage_number, spawn_obstacles=self.ENABLE_ENEMIES)
        self.add_widget(self.stage)
        if self.ENABLE_ENEMIES:
            self.spawn_initial_enemies()
        if self.ENABLE_PLAYER:
            self.remove_widget(self.player)
            self.player = Player(pos=(100, 0), health=self.initial_player_hp)
            self.player_health = self.player.health
            self.player_max_health = self.player.max_health
            self.player.bind(health=self.on_player_health_changed)
            self.add_widget(self.player)
            for enemy in self.stage.obstacles:
                enemy.target = self.player
                print(f"Restart: Set target for enemy at {enemy.pos} to player at {self.player.pos}")
        # ไม่เรียก self.spawn_portal() ที่นี่
        self.update_hp_hearts()  # Reset hearts