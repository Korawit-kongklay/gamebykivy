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
        """Spawn platforms with predefined positions for each stage."""
        platform_configs = {
            1: [  # Stage 1: Simple layout with a few platforms
                (200, 200),  # Middle-left platform
                (400, 250),  # Middle-right platform
                (600, 200),  # Far-right platform
                (300, 350),  # Upper-middle platform
            ],
            2: [  # Stage 2: More platforms, some vertical progression
                (150, 100),  # Lower-left
                (300, 200),  # Middle step
                (450, 300),  # Higher step
                (600, 200),  # Right-middle
                (200, 400),  # Upper-left
            ],
            3: [  # Stage 3: Zig-zag pattern
                (100, 150),  # Bottom-left
                (250, 250),  # Middle step up
                (400, 200),  # Middle step down
                (550, 300),  # Right step up
                (700, 250),  # Far-right step down
                (300, 400),  # Upper-middle
            ],
            4: [  # Stage 4: Complex layout with gaps
                (50, 100),   # Bottom-left
                (200, 150),  # Left step
                (350, 300),  # Middle-high
                (500, 200),  # Middle-right
                (650, 350),  # Right-high
                (150, 450),  # Upper-left
                (450, 500),  # Upper-middle
            ],
            5: [  # Stage 5: Challenging layout with spread platforms
                (50, 200),   # Left-middle
                (200, 300),  # Left-high step
                (350, 150),  # Middle-low
                (500, 350),  # Middle-high
                (650, 250),  # Right-middle
                (100, 500),  # Upper-left
                (300, 450),  # Upper-middle
                (600, 400),  # Upper-right
            ]
        }
    
        # Use predefined config for the current stage, fallback to random if stage > 5
        config = platform_configs.get(self.stage_number, [
            (random.randint(0, Window.width - 93), random.randint(0, Window.height - 24))
            for _ in range(8)  # Default to 8 random platforms if beyond stage 5
        ])
    
        self.platforms.clear()
        for x, y in config:
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