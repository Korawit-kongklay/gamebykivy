from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from .dino import Dino
from .stage import Stage

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
            self.dino = Dino(pos=(100, 0))  # Adjusted from (50, 0) for larger screen
            self.add_widget(self.dino)
        self.shoot_cooldown = 0.5
        self.last_shot_time = 0
        self.mouse_pos = (0, 0)

    def bind_inputs(self):
        self.keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self.keyboard.bind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        Window.bind(mouse_pos=self._on_mouse_pos)
        if self.ENABLE_BULLETS:
            Window.bind(on_mouse_down=self._on_mouse_down)

    def _keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up)
        self.keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if not self.game_active or not self.ENABLE_PLAYER or not self.dino:
            return False
        if keycode[1] == 'spacebar' and self.dino.y == 0:
            self.dino.velocity_y = 7  # Increased from 5 for taller screen
        elif keycode[1] in ('left', 'a'):
            self.dino.velocity_x = -5  # Increased from -3 for wider screen
        elif keycode[1] in ('right', 'd'):
            self.dino.velocity_x = 5  # Increased from 3 for wider screen
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
        bullet = PlayerBullet(start_pos=start_pos, target_pos=self.mouse_pos, speed=15)  # Increased speed
        self.add_widget(bullet)
        self.bullets.append(bullet)
        self.last_shot_time = Clock.get_time()

    def update(self, dt):
        if not self.game_active:
            return
        if self.ENABLE_PLAYER and self.dino:
            self.dino.velocity_y -= 0.15  # Slightly stronger gravity for taller screen
            self.dino.move()
        if self.ENABLE_BULLETS:
            for bullet in self.bullets[:]:
                bullet.move()
                if not (0 <= bullet.x <= Window.width and 0 <= bullet.y <= Window.height):
                    self.remove_widget(bullet)
                    self.bullets.remove(bullet)

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