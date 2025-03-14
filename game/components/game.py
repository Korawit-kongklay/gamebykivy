from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from .player import Player
from .stage import Stage
from .hitbox import Hitbox
from .boss import Boss
from .enemy import Enemy, FlyingEnemy
from .attack import ProjectileAttack
from .portal import Portal
import random
from components.music_manager import MusicManager

class Game(Widget):
    """Main game widget managing game state, entities, and interactions."""
    portal = ObjectProperty(None, allownone=True)
    player = ObjectProperty(None)
    stage = ObjectProperty(None)
    boss = ObjectProperty(None, allownone=True)
    score = NumericProperty(0)
    stage_number = NumericProperty(1)
    player_health = NumericProperty(20)
    player_max_health = NumericProperty(20)
    game_active = BooleanProperty(True)
    player_attacks = ListProperty([])
    enemy_attacks = ListProperty([])
    debug_hitbox = BooleanProperty(False)
    last_enemy_death_pos = ListProperty([0, 0])

    ENABLE_PLAYER = True
    ENABLE_ENEMIES = True
    ENABLE_ATTACKS = True
    ENABLE_BOSS = True
    MAX_STAGES = 5

    def __init__(self, music_manager=None, initial_player_hp=20, **kwargs):
        super().__init__(**kwargs)
        self.initial_player_hp = initial_player_hp
        self.hp_layout = None
        self.music_manager = music_manager if music_manager else MusicManager()
        self.walk_sound_playing = False
        self.restart_button = None
        self.end_game_label = None
        self.initialize_game()
        self.bind_inputs()
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.music_manager.play_music(self.stage_number)
        Window.bind(on_resize=self.on_window_resize)

    def initialize_game(self):
        """Initialize the game state and entities."""
        self.stage = Stage(stage_number=self.stage_number, spawn_obstacles=self.ENABLE_ENEMIES)
        self.add_widget(self.stage)
        if self.ENABLE_ENEMIES:
            self.spawn_initial_enemies()
            for enemy in self.stage.obstacles:
                self.music_manager.play_spawn()
        if self.ENABLE_PLAYER:
            scale_x = Window.width / 1280
            self.player = Player(pos=(100 * scale_x, 0), health=self.initial_player_hp)
            self.player_health = self.player.health
            self.player_max_health = self.player.max_health
            self.add_widget(self.player)
            self.player.bind(health=self.on_player_health_changed)
            self.music_manager.play_spawn()
            for enemy in self.stage.obstacles:
                enemy.target = self.player
        self.attack_cooldown = 0.5
        self.last_attack_time = 0
        self.mouse_pos = (0, 0)
        self.score = 0
        self.on_platform = False
        self.last_enemy_death_pos = [Window.width - 60, 10]
        try:
            self.hp_layout = self.ids.hp_layout
            self.hp_layout.bind(pos=self._update_hp_position)
        except AttributeError:
            print("Warning: hp_layout not found in ids. Ensure .kv file is properly set up.")
            self.hp_layout = None
        self.update_hp_hearts()
        if self.stage_number == 5 and self.ENABLE_BOSS and not self.boss:
            self.spawn_boss()

    def on_window_resize(self, window, width, height):
        """Handle window resize by updating all entities."""
        self.remove_widget(self.stage)
        self.stage = Stage(stage_number=self.stage_number, spawn_obstacles=self.ENABLE_ENEMIES)
        self.add_widget(self.stage)

        scale_x = width / 1280
        scale_y = height / 720
        if self.player:
            self.player.pos = (100 * scale_x, 0)
            self.player.size = (80 * scale_x, 80 * scale_y)

        if self.ENABLE_ENEMIES:
            self.stage.obstacles.clear()
            self.spawn_initial_enemies()

        if self.portal:
            self.remove_widget(self.portal)
            portal_x = max(0, min(self.last_enemy_death_pos[0] * scale_x, Window.width - 80 * scale_x))
            portal_y = max(0, min(self.last_enemy_death_pos[1] * scale_y, Window.height - 240 * scale_y))
            self.portal = Portal(pos=(portal_x, portal_y), player=self.player)
            self.add_widget(self.portal)

        if self.boss:
            self.boss.size = (60 * scale_x, 80 * scale_y)
            self.boss.pos = (Window.width - 60 * scale_x, self.boss.y)

        self.update_hp_hearts()
        self._update_restart_ui_positions()

    def spawn_initial_enemies(self):
        """Spawn initial enemies at random positions based on stage number, including FlyingEnemy."""
        enemy_count = 5 + (self.stage_number - 1)
        self.stage.obstacles.clear()
        scale_x = Window.width / 1280
        scale_y = Window.height / 720
        enemy_size = (80 * scale_x, 80 * scale_y)
        for _ in range(enemy_count):
            spawn_x = random.uniform(0, Window.width - enemy_size[0])
            spawn_y = random.uniform(0, Window.height - enemy_size[1])
            if random.random() < 0.3:
                enemy = FlyingEnemy(pos=(spawn_x, spawn_y), size=enemy_size)
            else:
                enemy = Enemy(pos=(spawn_x, spawn_y), size=enemy_size)
            self.stage.add_widget(enemy)
            self.stage.obstacles.append(enemy)
            if self.player:
                enemy.target = self.player

    def spawn_boss(self):
        """Spawn the boss in Stage 5."""
        scale_x = Window.width / 1280
        scale_y = Window.height / 720
        self.boss = Boss(pos=(Window.width - 60 * scale_x, 0))
        self.boss.size = (240 * scale_x, 240 * scale_y)
        self.boss.target = self.player
        self.add_widget(self.boss)
        self.boss.velocity_x = -1 * scale_x
        self.music_manager.play_spawn()

    def spawn_portal(self):
        """Spawn or reposition the portal at the last enemy death position."""
        if self.portal:
            self.remove_widget(self.portal)
        scale_x = Window.width / 1280
        scale_y = Window.height / 720
        portal_x = max(0, min(self.last_enemy_death_pos[0] * scale_x, Window.width - 80 * scale_x))
        portal_y = max(0, min(self.last_enemy_death_pos[1] * scale_y, Window.height - 240 * scale_y))
        self.portal = Portal(pos=(portal_x, portal_y), player=self.player)
        self.add_widget(self.portal)

    def _update_hp_position(self, instance, value):
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
        if keycode[1] == 'escape':
            self.game_active = False
            self.show_pause_menu()
            return True
        if keycode[1] == 'h':
            self.debug_hitbox = not self.debug_hitbox
            self.update_hitbox_visibility()
            return True
        if not self.ENABLE_PLAYER or not self.player:
            return False
        scale_x = Window.width / 1280
        scale_y = Window.height / 720
        if keycode[1] == 'spacebar':
            if self.can_jump(self.player):
                self.player.velocity_y = 9 * scale_y
                self.music_manager.play_jump()
        elif keycode[1] in ('left', 'a'):
            self.player.velocity_x = -5 * scale_x
            if not self.walk_sound_playing and self.on_platform:
                self.music_manager.play_walk()
                self.walk_sound_playing = True
        elif keycode[1] in ('right', 'd'):
            self.player.velocity_x = 5 * scale_x
            if not self.walk_sound_playing and self.on_platform:
                self.music_manager.play_walk()
                self.walk_sound_playing = True
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        if self.ENABLE_PLAYER and self.player and keycode[1] in ('left', 'a', 'right', 'd'):
            self.player.velocity_x = 0
            self.walk_sound_playing = False
        return True

    def _on_mouse_pos(self, window, pos):
        self.mouse_pos = pos

    def _on_mouse_down(self, window, x, y, button, modifiers):
        if button != 'left' or not self.game_active or (Clock.get_time() - self.last_attack_time < self.attack_cooldown):
            return
        scale_x = Window.width / 1280
        start_pos = (self.player.x + self.player.width, self.player.y + self.player.height / 2)
        attack = ProjectileAttack(start_pos=start_pos, target_pos=self.mouse_pos, speed=15 * scale_x)
        self.add_widget(attack)
        self.player_attacks.append(attack)
        self.last_attack_time = Clock.get_time()
        self.music_manager.play_shoot()

    def on_player_health_changed(self, instance, value):
        self.player_health = value
        self.update_hp_hearts()

    def update_hp_hearts(self):
        if not self.hp_layout:
            return
        self.hp_layout.clear_widgets()
        scale_x = Window.width / 1280
        max_hearts = int(self.player_max_health / 2)
        full_hearts = int(self.player_health / 2)
        half_heart = self.player_health % 2 == 1
        for _ in range(full_hearts):
            heart = Image(source='assets/images/full_heart.png', size=(50 * scale_x, 50 * scale_x), allow_stretch=True, keep_ratio=False)
            self.hp_layout.add_widget(heart)
        if half_heart:
            half = Image(source='assets/images/half_heart.png', size=(50 * scale_x, 50 * scale_x), allow_stretch=True, keep_ratio=False)
            self.hp_layout.add_widget(half)
        remaining_hearts = max_hearts - full_hearts - (1 if half_heart else 0)
        for _ in range(remaining_hearts):
            blank = Image(source='assets/images/blank_heart.png', size=(50 * scale_x, 50 * scale_x), allow_stretch=True, keep_ratio=False)
            self.hp_layout.add_widget(blank)

    def _update_restart_ui_positions(self):
        """Update positions of restart button and end game label on window resize."""
        if self.restart_button:
            self.restart_button.pos = (Window.width / 2 - 150, Window.height / 2 - 50)
        if self.end_game_label:
            self.end_game_label.pos = (Window.width / 2 - 150, Window.height / 2 + 75)

    def show_restart_button(self, game_over=False, game_completed=False):
        """Show a large restart button and end-game message in the center of the screen."""
        if self.restart_button:
            self.remove_widget(self.restart_button)
            self.restart_button = None
        if self.end_game_label:
            self.remove_widget(self.end_game_label)
            self.end_game_label = None
        
        self.end_game_label = Label(
            text='Victory!' if game_completed else 'Game Over!',
            font_size=100,
            size_hint=(None, None),
            size=(300, 100),
            pos=(Window.width / 2 - 150, Window.height / 2 + 75),
            color=(0, 1, 0, 1) if game_completed else (1, 0, 0, 1)
        )
        self.add_widget(self.end_game_label)
        
        self.restart_button = Button(
            text='Restart Game',
            size_hint=(None, None),
            size=(300, 100),
            pos=(Window.width / 2 - 150, Window.height / 2 - 50),
            font_size=30,
            background_color=(0, 1, 0, 1) if game_completed else (1, 0, 0, 1)
        )
        
        if game_over:
            self.restart_button.bind(on_press=lambda instance: self.restart(game_over=True))
        elif game_completed:
            self.restart_button.bind(on_press=lambda instance: self.restart(game_completed=True))
        else:
            self.restart_button.bind(on_press=lambda instance: self.restart())
        
        self.add_widget(self.restart_button)

    def update(self, dt):
        if not self.game_active:
            return

        if self.ENABLE_PLAYER and self.player:
            self.apply_gravity(self.player)
            self.player.move()
            self.on_platform = self.handle_platform_collision(self.player)
            self.player_health = self.player.health
            if self.debug_hitbox:
                self.player.update_hitbox_debug()

        if self.ENABLE_ENEMIES and len(self.stage.obstacles) == 0 and not self.boss and not self.portal:
            self.spawn_portal()

        if self.boss:
            self.apply_gravity(self.boss)
            self.boss.move()
            self.boss.update(self, dt)
            self.handle_platform_collision(self.boss)
            if self.boss.x < 0:
                self.boss.x = 0
            if self.boss.health <= 0 and not self.portal:
                self.spawn_portal()
            if self.debug_hitbox:
                self.boss.update_hitbox_debug()

        if self.ENABLE_ATTACKS:
            self.update_attacks()

        if self.ENABLE_ENEMIES:
            self.update_enemies()

        if self.portal and self.player and Hitbox.collide(self.player.get_hitbox_rect(), self.portal.get_hitbox_rect()):
            self.next_stage()

        if self.stage_number == 1 and self.ENABLE_ENEMIES and len(self.stage.obstacles) == 0 and not self.boss and not self.portal:
            self.spawn_portal()

        if self.stage_number == self.MAX_STAGES and not self.stage.obstacles and not self.boss:
            self.game_active = False
            self.music_manager.fade_out_music(duration=1.0)
            self.show_restart_button(game_completed=True)

        if self.player_health <= 0:
            self.game_active = False
            self.music_manager.play_die()
            self.music_manager.fade_out_music(duration=1.0)
            self.show_restart_button(game_over=True)

    def next_stage(self):
        if self.stage_number >= self.MAX_STAGES:
            return
        self.stage_number += 1
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
                self.music_manager.play_spawn()
        if self.ENABLE_PLAYER:
            scale_x = Window.width / 1280
            self.player.pos = (100 * scale_x, 0)
            self.player.velocity_x = 0
            self.player.velocity_y = 0
        self.update_hp_hearts()
        self.music_manager.play_music(self.stage_number)
        if self.stage_number == 5 and self.ENABLE_BOSS and not self.boss:
            self.spawn_boss()

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
        entity.velocity_y -= 0.15 * (Window.height / 720)

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
        scale_x = Window.width / 1280
        for attack in self.player_attacks[:]:
            attack.move()
            attack_rect = attack.get_hitbox_rect()
            if not (0 <= attack.x <= Window.width and 0 <= attack.y <= Window.height):
                try:
                    self.remove_widget(attack)
                    self.player_attacks.remove(attack)
                except Exception as e:
                    print(f"Error removing player attack: {e}")
            else:
                if self.boss and Hitbox.collide(attack_rect, self.boss.get_hitbox_rect()):
                    self.boss.health -= 1
                    try:
                        self.remove_widget(attack)
                        self.player_attacks.remove(attack)
                    except Exception as e:
                        print(f"Error removing player attack: {e}")
                    if self.boss.health <= 0:
                        try:
                            self.remove_widget(self.boss)
                            self.boss = None
                            self.score += 50
                        except Exception as e:
                            print(f"Error removing boss: {e}")
                elif self.ENABLE_ENEMIES:
                    for enemy in self.stage.obstacles[:]:
                        enemy_rect = enemy.get_hitbox_rect()
                        if Hitbox.collide(attack_rect, enemy_rect):
                            enemy.take_damage(100)
                            try:
                                self.remove_widget(attack)
                                self.player_attacks.remove(attack)
                            except Exception as e:
                                print(f"Error removing player attack: {e}")
                            if enemy.health <= 0:
                                self.score += 100
                                self.last_enemy_death_pos = [enemy.x / scale_x, enemy.y / (Window.height / 720)]
                            break

        for attack in self.enemy_attacks[:]:
            attack.move()
            attack_rect = attack.get_hitbox_rect()
            if not (0 <= attack.x <= Window.width and 0 <= attack.y <= Window.height):
                try:
                    self.remove_widget(attack)
                    self.enemy_attacks.remove(attack)
                except Exception as e:
                    print(f"Error removing enemy attack: {e}")
            elif Hitbox.collide(attack_rect, self.player.get_hitbox_rect()):
                self.player.take_damage(1)
                try:
                    self.remove_widget(attack)
                    self.enemy_attacks.remove(attack)
                except Exception as e:
                    print(f"Error removing enemy attack: {e}")

        collisions = []
        for player_attack in self.player_attacks[:]:
            player_attack_rect = player_attack.get_hitbox_rect()
            for enemy_attack in self.enemy_attacks[:]:
                enemy_attack_rect = enemy_attack.get_hitbox_rect()
                if Hitbox.collide(player_attack_rect, enemy_attack_rect):
                    collisions.append((player_attack, enemy_attack))
                    break

        for player_attack, enemy_attack in collisions:
            try:
                if player_attack in self.player_attacks:
                    self.remove_widget(player_attack)
                    self.player_attacks.remove(player_attack)
                if enemy_attack in self.enemy_attacks:
                    self.remove_widget(enemy_attack)
                    self.enemy_attacks.remove(enemy_attack)
            except Exception as e:
                print(f"Error handling collision: {e}")

    def update_enemies(self):
        for enemy in self.stage.obstacles[:]:
            if isinstance(enemy, FlyingEnemy):
                enemy.move()
            else:
                self.apply_gravity(enemy)
                enemy.move()
                self.handle_platform_collision(enemy)
            if Hitbox.collide(self.player.get_hitbox_rect(), enemy.get_hitbox_rect()):
                self.player.take_damage(1)
                scale_x = Window.width / 1280
                scale_y = Window.height / 720
                self.last_enemy_death_pos = [enemy.x / scale_x, enemy.y / scale_y]
                self.stage.remove_widget(enemy)
                self.stage.obstacles.remove(enemy)
            elif enemy.x < -enemy.width:
                self.stage.remove_widget(enemy)
                self.stage.obstacles.remove(enemy)
            if self.debug_hitbox:
                enemy.update_hitbox_debug()

    def restart(self, game_over=False, game_completed=False):
        """
        Restart the game with appropriate messaging based on game state.
        
        Args:
            game_over (bool): True if restarting due to player death
            game_completed (bool): True if restarting after clearing all stages
        """
        if self.restart_button:
            self.remove_widget(self.restart_button)
            self.restart_button = None
        if self.end_game_label:
            self.remove_widget(self.end_game_label)
            self.end_game_label = None
        
        self.music_manager.fade_out_music(duration=0.5)
        
        if game_over:
            print("Game Over! Restarting game...")
        elif game_completed:
            print(f"Congratulations! You've cleared all {self.MAX_STAGES} stages! Restarting game...")
        else:
            print("Restarting game...")

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
            for enemy in self.stage.obstacles:
                enemy.target = self.player
                self.music_manager.play_spawn()
        
        if self.ENABLE_PLAYER:
            self.remove_widget(self.player)
            scale_x = Window.width / 1280
            scale_y = Window.height / 720
            self.player = Player(pos=(100 * scale_x, 0), health=self.initial_player_hp)
            self.player.size = (80 * scale_x, 80 * scale_y)
            self.player_health = self.player.health
            self.player_max_health = self.player.max_health
            self.player.bind(health=self.on_player_health_changed)
            self.add_widget(self.player)
            for enemy in self.stage.obstacles:
                enemy.target = self.player
        
        self.last_enemy_death_pos = [Window.width - 60, 10]
        
        self.update_hp_hearts()
        
        Clock.schedule_once(lambda dt: self.music_manager.play_music(self.stage_number), 0.6)

    def show_pause_menu(self):
        from .pause_menu import PauseMenu
        app = App.get_running_app()
        app.root.clear_widgets()
        pause_menu = PauseMenu(self)
        app.root.add_widget(pause_menu)