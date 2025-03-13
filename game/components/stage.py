from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock
import random
from .platform import Platform
from .enemy import Enemy
from .hitbox import Hitbox
from kivy.core.window import Window
from kivy.vector import Vector

class Stage(Widget):
    stage_number = NumericProperty(1)
    obstacles = ListProperty([])  # Holds Enemy instances
    platforms = ListProperty([])

    def __init__(self, stage_number=1, spawn_obstacles=False, **kwargs):
        super().__init__(**kwargs)
        self.stage_number = stage_number
        self.spawn_obstacles_enabled = spawn_obstacles
        self.spawn_platforms()
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        # Bind to window size changes
        Window.bind(on_resize=self.on_window_resize)

    def spawn_platforms(self):
        """Spawn platforms with positions and sizes relative to window dimensions."""
        # Base window size for original coordinates (assumed 1280x720 from main_menu.py)
        base_width = 1280
        base_height = 720

        # Original fixed configuration
        platform_config = [
            (200, 246),
            (754, 554),
            (700, 424),
            (461, 614),
            (812, 649),
            (245, 424),
            (374, 187),
            (844, 68),
            (835, 424),
            (1029, 343),
            (521, 89),
            (1111, 442),
            (420, 259),
            (294, 598),
            (681, 349),
            (640, 160),
            (35, 275),
            (438, 426),
            (80, 387),
            (997, 115),
        ]

        self.platforms.clear()
        # Calculate scaling factors based on current window size
        width_scale = Window.width / base_width
        height_scale = Window.height / base_height
        # Base platform size (93, 24) scaled dynamically
        platform_width = 93 * width_scale
        platform_height = 24 * height_scale

        for base_x, base_y in platform_config:
            # Scale positions
            x = base_x * width_scale
            y = base_y * height_scale
            # Ensure platforms stay within bounds
            x = min(max(x, 0), Window.width - platform_width)
            y = min(max(y, 0), Window.height - platform_height)
            platform = Platform(pos=(x, y), size=(platform_width, platform_height))
            self.add_widget(platform)
            self.platforms.append(platform)

    def on_window_resize(self, window, width, height):
        """Update platform positions and sizes when window is resized."""
        self.spawn_platforms()  # Respawn platforms with new scaling

    def spawn_obstacles(self, dt=None):
        """Spawn one enemy with minimum separation."""
        if not self.spawn_obstacles_enabled:
            return
        min_separation = 150 * (Window.width / 1280)  # Scale separation dynamically
        attempts = 0
        max_attempts = 10
        while attempts < max_attempts:
            x = random.uniform(0, Window.width - 50)
            y = random.uniform(50, Window.height - 50)
            too_close = False
            for enemy in self.obstacles:
                dx = enemy.x - x
                dy = enemy.y - y
                if Vector(dx, dy).length() < min_separation:
                    too_close = True
                    break
            if not too_close:
                enemy = Enemy()
                enemy.x = x
                enemy.y = y
                self.add_widget(enemy)
                self.obstacles.append(enemy)
                print(f"Spawned enemy at {enemy.pos}, parent: {enemy.parent}")
                break
            attempts += 1

    def update(self, dt):
        if not self.spawn_obstacles_enabled:
            return
        for enemy in self.obstacles[:]:
            if enemy.x < -enemy.width:
                self.remove_widget(enemy)
                self.obstacles.remove(enemy)

    def check_platform_collision(self, entity):
        entity_rect = entity.get_hitbox_rect()
        for platform in self.platforms:
            plat_rect = platform.get_hitbox_rect()
            if Hitbox.collide(entity_rect, plat_rect) and entity.velocity_y <= 0:
                entity_prev_y = entity.y + entity.velocity_y
                if entity_prev_y + entity_rect['height'] > plat_rect['top']:
                    distance = plat_rect['top'] - entity_rect['y']
                    if -5 <= distance <= 10:
                        entity.y = plat_rect['top'] - entity.hitbox.offset_y
                        entity.velocity_y = 0
                        return True
        return False