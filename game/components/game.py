from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from .player import Player
from .stage import Stage
from .hitbox import Hitbox
from .boss import Boss


class Game(Widget):
    """Main game widget managing game state, entities, and interactions."""

    player = ObjectProperty(None)
    stage = ObjectProperty(None)
    boss = ObjectProperty(None)
    score = NumericProperty(0)
    stage_number = NumericProperty(1)
    health = NumericProperty(3)
    game_active = BooleanProperty(True)
    player_attacks = ListProperty([])  # Player-initiated attacks
    enemy_attacks = ListProperty([])  # Enemy-initiated attacks
    debug_hitbox = BooleanProperty(False)  # Toggle for hitbox debugging

    # Game feature toggles
    ENABLE_PLAYER = True
    ENABLE_OBSTACLES = False
    ENABLE_ATTACKS = True
    ENABLE_BOSS = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialize_game()
        self.bind_inputs()
        # Schedule updates
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        if self.ENABLE_BOSS:
            Clock.schedule_interval(self.spawn_boss_check, 5.0)

    def initialize_game(self):
        """Initialize the game state and entities."""
        self.stage = Stage(stage_number=self.stage_number, spawn_obstacles=self.ENABLE_OBSTACLES)
        self.add_widget(self.stage)
        if self.ENABLE_PLAYER:
            self.player = Player(pos=(100, 0))
            self.add_widget(self.player)
        self.attack_cooldown = 0.5
        self.last_attack_time = 0
        self.boss_attack_cooldown = 2.0
        self.last_boss_attack = 0
        self.mouse_pos = (0, 0)
        self.score = 0
        self.health = 3

    def bind_inputs(self):
        """Bind keyboard and mouse inputs for player control."""
        self.keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self.keyboard.bind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        Window.bind(mouse_pos=self._on_mouse_pos)
        if self.ENABLE_ATTACKS:
            Window.bind(on_mouse_down=self._on_mouse_down)

    def _keyboard_closed(self):
        """Handle keyboard closure."""
        self.keyboard.unbind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        self.keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Handle key press events."""
        if not self.game_active:
            return False

        # Toggle hitbox debugging with 'H' key
        if keycode[1] == 'h':
            self.debug_hitbox = not self.debug_hitbox
            self.update_hitbox_visibility()
            return True

        if not self.ENABLE_PLAYER or not self.player:
            return False
        if keycode[1] == 'spacebar':
            if self.can_jump(self.player):
                self.player.velocity_y = 7
        elif keycode[1] in ('left', 'a'):
            self.player.velocity_x = -5
        elif keycode[1] in ('right', 'd'):
            self.player.velocity_x = 5
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        """Handle key release events."""
        if self.ENABLE_PLAYER and self.player and keycode[1] in ('left', 'a', 'right', 'd'):
            self.player.velocity_x = 0
        return True

    def _on_mouse_pos(self, window, pos):
        """Track mouse position."""
        self.mouse_pos = pos

    def _on_mouse_down(self, window, x, y, button, modifiers):
        """Handle mouse click events for attacks."""
        from .attack import ProjectileAttack
        if button != 'left' or not self.game_active or (Clock.get_time() - self.last_attack_time < self.attack_cooldown):
            return
        start_pos = (self.player.x + self.player.width, self.player.y + self.player.height / 2)
        attack = ProjectileAttack(start_pos=start_pos, target_pos=self.mouse_pos, speed=15)
        self.add_widget(attack)
        self.player_attacks.append(attack)
        self.last_attack_time = Clock.get_time()

    def spawn_boss_check(self, dt):
        """Check if a boss should spawn based on score."""
        if not self.ENABLE_BOSS or not self.game_active:
            return
        if not self.boss and self.score >= 10:
            self.boss = Boss(pos=(Window.width - 60, 0))
            self.add_widget(self.boss)
            self.boss.velocity_x = -1

    def update(self, dt):
        """Update game state each frame."""
        if not self.game_active:
            return

        self.score += dt

        if self.ENABLE_PLAYER and self.player:
            self.apply_gravity(self.player)
            self.player.move()
            self.handle_platform_collision(self.player)
            if self.debug_hitbox:
                self.player.update_hitbox_debug()

        if self.boss:
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

        if self.ENABLE_OBSTACLES:
            self.check_obstacle_collisions()

        if self.health <= 0:
            self.game_active = False
            print("Game Over!")

    def update_hitbox_visibility(self):
        """Update visibility of hitboxes for all entities."""
        if self.player:
            self.player.toggle_hitbox_debug(self.debug_hitbox)
        for platform in self.stage.platforms:
            platform.toggle_hitbox_debug(self.debug_hitbox)
        if self.boss:
            self.boss.toggle_hitbox_debug(self.debug_hitbox)

    def apply_gravity(self, entity):
        """Apply gravity to an entity."""
        entity.velocity_y -= 0.15

    def can_jump(self, entity):
        """Check if an entity can jump."""
        on_ground = entity.y == 0
        on_platform = self.is_on_platform(entity)
        return (on_ground or on_platform) and abs(entity.velocity_y) < 0.01

    def is_on_platform(self, entity):
        """Check if an entity is on a platform."""
        entity_rect = entity.get_hitbox_rect()
        for platform in self.stage.platforms:
            plat_rect = platform.get_hitbox_rect()
            if Hitbox.collide(entity_rect, plat_rect) and entity.velocity_y <= 0:
                distance = plat_rect['top'] - entity_rect['y']
                if -5 <= distance <= 10:
                    return True
        return False

    def handle_platform_collision(self, entity):
        """Handle collision between an entity and platforms."""
        entity_rect = entity.get_hitbox_rect()
        for platform in self.stage.platforms:
            plat_rect = platform.get_hitbox_rect()
            if Hitbox.collide(entity_rect, plat_rect) and entity.velocity_y <= 0:
                entity.y = plat_rect['top'] - entity.hitbox.offset_y
                entity.velocity_y = 0
                return True
        if entity.y <= 0:
            entity.y = 0
            entity.velocity_y = 0
            return True
        return False

    def update_attacks(self):
        """Update player and enemy attacks."""
        for attack in self.player_attacks[:]:
            attack.move()
            if not (0 <= attack.x <= Window.width and 0 <= attack.y <= Window.height):
                self.remove_widget(attack)
                self.player_attacks.remove(attack)
            elif self.boss and Hitbox.collide(attack.get_hitbox_rect(), self.boss.get_hitbox_rect()):
                self.boss.health -= 1
                self.remove_widget(attack)
                self.player_attacks.remove(attack)
                if self.boss.health <= 0:
                    self.remove_widget(self.boss)
                    self.boss = None
                    self.score += 50

        for attack in self.enemy_attacks[:]:
            attack.move()
            if not (0 <= attack.x <= Window.width and 0 <= attack.y <= Window.height):
                self.remove_widget(attack)
                self.enemy_attacks.remove(attack)
            elif Hitbox.collide(attack.get_hitbox_rect(), self.player.get_hitbox_rect()):
                self.health -= 1
                self.remove_widget(attack)
                self.enemy_attacks.remove(attack)

    def check_obstacle_collisions(self):
        """Check collisions between player and obstacles."""
        for obstacle in self.stage.obstacles[:]:
            if Hitbox.collide(self.player.get_hitbox_rect(), obstacle.get_hitbox_rect()):
                self.health -= 1
                self.stage.remove_widget(obstacle)
                self.stage.obstacles.remove(obstacle)

    def restart(self):
        """Restart the game to initial state."""
        self.game_active = True
        self.score = 0
        self.stage_number = 1
        self.health = 3
        self.player_attacks.clear()
        self.enemy_attacks.clear()
        if self.boss:
            self.remove_widget(self.boss)
            self.boss = None
        self.remove_widget(self.stage)
        self.stage = Stage(stage_number=self.stage_number, spawn_obstacles=self.ENABLE_OBSTACLES)
        self.add_widget(self.stage)
        if self.ENABLE_PLAYER:
            self.remove_widget(self.player)
            self.player = Player(pos=(100, 0))
            self.add_widget(self.player)