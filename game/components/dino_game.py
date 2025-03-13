from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from .dino import Dino
from .stage import Stage
from .hitbox import Hitbox

class DinoGame(Widget):
    dino = ObjectProperty(None)
    stage = ObjectProperty(None)
    score = NumericProperty(0)
    stage_number = NumericProperty(1)
    health = NumericProperty(3)
    game_active = BooleanProperty(True)
    bullets = ListProperty([])

    ENABLE_PLAYER = True
    ENABLE_OBSTACLES = False
    ENABLE_BULLETS = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialize_game()
        self.bind_inputs()
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def initialize_game(self):
        self.stage = Stage(stage_number=self.stage_number, spawn_obstacles=self.ENABLE_OBSTACLES)
        self.add_widget(self.stage)
        if self.ENABLE_PLAYER:
            self.dino = Dino(pos=(100, 0))
            self.add_widget(self.dino)
        self.shoot_cooldown = 0.5
        self.last_shot_time = 0
        self.mouse_pos = (0, 0)

    def bind_inputs(self):
        self.keyboard = Window.request_keyboard(self._keyboard_closed, self)
        print(f"Keyboard bound: {self.keyboard is not None}")
        self.keyboard.bind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        Window.bind(mouse_pos=self._on_mouse_pos)
        if self.ENABLE_BULLETS:
            Window.bind(on_mouse_down=self._on_mouse_down)

    def _keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        self.keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if not self.game_active or not self.ENABLE_PLAYER or not self.dino:
            print("Jump blocked - Game not active or no dino")
            return False
        print(f"Key pressed: {keycode[1]}")
        if keycode[1] == 'spacebar':
            on_ground = self.dino.y == 0
            on_platform = self.is_on_platform(self.dino)
            can_jump = (on_ground or on_platform) and abs(self.dino.velocity_y) < 0.01
            print(f"Jump attempt - On ground: {on_ground}, On platform: {on_platform}, Vel_y: {self.dino.velocity_y}, Can jump: {can_jump}")
            if can_jump:
                self.dino.velocity_y = 7
                print("Jumping initiated!")
        elif keycode[1] in ('left', 'a'):
            self.dino.velocity_x = -5
        elif keycode[1] in ('right', 'd'):
            self.dino.velocity_x = 5
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        if self.ENABLE_PLAYER and self.dino and keycode[1] in ('left', 'a', 'right', 'd'):
            self.dino.velocity_x = 0
        return True

    def _on_mouse_pos(self, window, pos):
        self.mouse_pos = pos

    def _on_mouse_down(self, window, x, y, button, modifiers):
        from .bullet import PlayerBullet
        if button != 'left' or not self.game_active or (Clock.get_time() - self.last_shot_time < self.shoot_cooldown):
            return
        start_pos = (self.dino.x + self.dino.width, self.dino.y + self.dino.height / 2)
        bullet = PlayerBullet(start_pos=start_pos, target_pos=self.mouse_pos, speed=15)
        self.add_widget(bullet)
        self.bullets.append(bullet)
        self.last_shot_time = Clock.get_time()

    def update(self, dt):
        if not self.game_active:
            return
        if self.ENABLE_PLAYER and self.dino:
            self.dino.velocity_y -= 0.15  # Gravity
            prev_y = self.dino.y
            self.dino.move()
            landed = self.check_platform_collision(self.dino)
            print(f"Update - Pos: ({self.dino.x}, {self.dino.y}), Prev_y: {prev_y}, Vel_y: {self.dino.velocity_y}, Landed: {landed}")
        if self.ENABLE_BULLETS:
            for bullet in self.bullets[:]:
                bullet.move()
                if not (0 <= bullet.x <= Window.width and 0 <= bullet.y <= Window.height):
                    self.remove_widget(bullet)
                    self.bullets.remove(bullet)

    def is_on_platform(self, character):
        """Check if the character is on a platform without modifying state."""
        char_rect = character.get_hitbox_rect()
        print(f"Char hitbox: x={char_rect['x']}, y={char_rect['y']}, w={char_rect['width']}, h={char_rect['height']}, top={char_rect['top']}")
        for platform in self.stage.platforms:
            plat_rect = platform.get_hitbox_rect()
            print(f"Plat hitbox: x={plat_rect['x']}, y={plat_rect['y']}, w={plat_rect['width']}, h={plat_rect['height']}, top={plat_rect['top']}")
            colliding = Hitbox.collide(char_rect, plat_rect)
            distance = plat_rect['top'] - char_rect['y']
            is_on = colliding and character.velocity_y <= 0 and -5 <= distance <= 10
            print(f"is_on_platform - Colliding: {colliding}, Distance: {distance}, Is on: {is_on}")
            if is_on:
                return True
        return False

    def check_platform_collision(self, character):
        """Handle collision and position adjustment."""
        char_rect = character.get_hitbox_rect()
        for platform in self.stage.platforms:
            plat_rect = platform.get_hitbox_rect()
            if Hitbox.collide(char_rect, plat_rect) and character.velocity_y <= 0:
                character.y = plat_rect['top'] - character.hitbox.offset_y
                character.velocity_y = 0
                print(f"Collision - Landed on platform, y set to: {character.y}, Plat top: {plat_rect['top']}")
                return True
        
        # Ground check
        if character.y <= 0:
            character.y = 0
            character.velocity_y = 0
            print("Collision - Landed on ground")
            return True
        return False

    def restart(self):
        self.game_active = True
        self.score = 0
        self.stage_number = 1
        self.health = 3
        self.bullets.clear()
        self.remove_widget(self.stage)
        self.stage = Stage(stage_number=self.stage_number, spawn_obstacles=self.ENABLE_OBSTACLES)
        self.add_widget(self.stage)
        if self.ENABLE_PLAYER:
            self.remove_widget(self.dino)
            self.dino = Dino(pos=(100, 0))
            self.add_widget(self.dino)