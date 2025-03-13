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
        (200, 100),  # Middle-left platform (200 - 100 = 100)
        (400, 150),  # Middle-right platform (250 - 100 = 150)
        (600, 100),  # Far-right platform (200 - 100 = 100)
        (300, 250),  # Upper-middle platform (350 - 100 = 250)
    ],
    2: [  # Stage 2: More platforms, some vertical progression
        (150, 0),    # Lower-left (100 - 100 = 0)
        (300, 100),  # Middle step (200 - 100 = 100)
        (450, 200),  # Higher step (300 - 100 = 200)
        (600, 100),  # Right-middle (200 - 100 = 100)
        (200, 300),  # Upper-left (400 - 100 = 300)
    ],
    3: [  # Stage 3: Zig-zag pattern
        (100, 50),   # Bottom-left (150 - 100 = 50)
        (250, 150),  # Middle step up (250 - 100 = 150)
        (400, 100),  # Middle step down (200 - 100 = 100)
        (550, 200),  # Right step up (300 - 100 = 200)
        (700, 150),  # Far-right step down (250 - 100 = 150)
        (300, 300),  # Upper-middle (400 - 100 = 300)
    ],
    4: [  # Stage 4: Complex layout with gaps
        (50, 0),     # Bottom-left (100 - 100 = 0)
        (200, 50),   # Left step (150 - 100 = 50)
        (350, 200),  # Middle-high (300 - 100 = 200)
        (500, 100),  # Middle-right (200 - 100 = 100)
        (650, 250),  # Right-high (350 - 100 = 250)
        (150, 350),  # Upper-left (450 - 100 = 350)
        (450, 400),  # Upper-middle (500 - 100 = 400)
    ],
    5: [  # Stage 5: Challenging layout with spread platforms
        (50, 100),   # Left-middle (200 - 100 = 100)
        (200, 200),  # Left-high step (300 - 100 = 200)
        (350, 50),   # Middle-low (150 - 100 = 50)
        (500, 250),  # Middle-high (350 - 100 = 250)
        (650, 150),  # Right-middle (250 - 100 = 150)
        (100, 400),  # Upper-left (500 - 100 = 400)
        (300, 350),  # Upper-middle (450 - 100 = 350)
        (600, 300),  # Upper-right (400 - 100 = 300)
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