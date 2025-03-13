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

    def spawn_platforms(self):
        platform_configs = {
            1: [(200, 200), (293, 150), (386, 150), (479, 100), (450, 250), (543, 250), (100, 350), (193, 350), (286, 350)],
            2: [(150, 100), (400, 200), (300, 350), (600, 300)]
        }.get(self.stage_number, [
            (random.randint(0, Window.width - 93), random.randint(0, Window.height - 24)),
            (random.randint(0, Window.width - 93), random.randint(0, Window.height - 24)),
            (random.randint(0, Window.width - 93), random.randint(0, Window.height - 24)),
            (random.randint(0, Window.width - 93), random.randint(0, Window.height - 24)),
            (random.randint(0, Window.width - 93), random.randint(0, Window.height - 24)),
            (random.randint(0, Window.width - 93), random.randint(0, Window.height - 24)),
            (random.randint(0, Window.width - 93), random.randint(0, Window.height - 24)),
            (random.randint(0, Window.width - 93), random.randint(0, Window.height - 24)),
        ])

        self.platforms.clear()
        for x, y in platform_configs:
            platform = Platform(pos=(x, y), size=(93, 24))
            self.add_widget(platform)
            self.platforms.append(platform)

    def spawn_obstacles(self, dt=None):
        """Spawn one enemy with minimum separation."""
        if not self.spawn_obstacles_enabled:
            return
        min_separation = 150
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