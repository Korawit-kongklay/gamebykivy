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
        """Spawn platforms with a fixed configuration for all stages."""
        platform_config = [
            # Using Stage 1's configuration for all stages (~21 platforms)
            (200, 100),
            (293, 100),  
            (400, 150),  
            (600, 100),
            (693, 76),  
            (300, 250),
            (393, 274),  
            (486, 298),
            (765, 298),
            (858, 274),  
            (700, 500),
            (607, 500),
            (514, 500),
            (421, 500),   
            (0, 400),
            (93, 400),
            (186, 424),
            (1187, 576),
            (1187, 176),
            (1094, 152),
            (1001, 128),
            (1094, 552),
            (1001, 528),
            (908, 528),
        ]

        self.platforms.clear()
        for x, y in platform_config:
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