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

    # Platform generation constants
    BASE_WIDTH = 1280
    BASE_HEIGHT = 720
    PLATFORM_WIDTH = 93
    PLATFORM_HEIGHT = 24
    BUFFER_ZONE = 20  # Minimum distance between platforms
    NUM_PLATFORMS = 15
    MAX_ATTEMPTS = 1000

    def __init__(self, stage_number=1, spawn_obstacles=False, **kwargs):
        super().__init__(**kwargs)
        self.stage_number = stage_number
        self.spawn_obstacles_enabled = spawn_obstacles
        self.spawn_platforms()
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        # Bind to window size changes
        Window.bind(on_resize=self.on_window_resize)

    def spawn_platforms(self):
        """Spawn random platforms with positions and sizes relative to window dimensions."""
        self.platforms.clear()

        # Calculate scaling factors based on current window size
        width_scale = Window.width / self.BASE_WIDTH
        height_scale = Window.height / self.BASE_HEIGHT
        platform_width = self.PLATFORM_WIDTH * width_scale
        platform_height = self.PLATFORM_HEIGHT * height_scale
        buffer_zone = self.BUFFER_ZONE * width_scale  # Scale buffer zone dynamically

        # Define max_y to avoid overlapping with HP layout (55) and Score Label (25)
        max_y = Window.height - (55 * height_scale + 25 * height_scale)  # Buffer for HP (55) + Label (25)

        # Generate random platforms
        platforms = self.generate_random_platforms(
            num_platforms=self.NUM_PLATFORMS,
            platform_width=platform_width,
            platform_height=platform_height,
            buffer_zone=buffer_zone,
            max_y=max_y
        )

        # Add platforms to the stage
        for x, y in platforms:
            platform = Platform(pos=(x, y), size=(platform_width, platform_height))
            self.add_widget(platform)
            self.platforms.append(platform)

        print(f"Stage {self.stage_number}: Generated {len(platforms)} platforms")

    def generate_random_platforms(self, num_platforms, platform_width, platform_height, buffer_zone, max_y):
        """Generate random, non-overlapping platform positions with a maximum y limit."""
        platforms = []

        for _ in range(num_platforms):
            attempts = 0
            while attempts < self.MAX_ATTEMPTS:
                # Generate positions within window bounds, accounting for buffer and max_y
                x = random.uniform(buffer_zone, Window.width - platform_width - buffer_zone)
                y = random.uniform(buffer_zone, max_y - platform_height - buffer_zone)  # Limit y to max_y
                new_platform = (x, y)

                if not self.check_overlap(new_platform, platforms, platform_width, platform_height, buffer_zone):
                    platforms.append(new_platform)
                    break

                attempts += 1

            if attempts >= self.MAX_ATTEMPTS:
                print(f"Stage {self.stage_number}: Could only place {len(platforms)} platforms due to spacing constraints")
                break

        return platforms

    def check_overlap(self, new_platform, existing_platforms, platform_width, platform_height, buffer_zone):
        """Check if new_platform overlaps with or is too close to existing platforms."""
        new_x, new_y = new_platform
        new_right = new_x + platform_width + buffer_zone
        new_top = new_y + platform_height + buffer_zone
        new_left = new_x - buffer_zone
        new_bottom = new_y - buffer_zone

        for (x, y) in existing_platforms:
            right = x + platform_width + buffer_zone
            top = y + platform_height + buffer_zone
            left = x - buffer_zone
            bottom = y - buffer_zone

            # Check if rectangles (with buffer) overlap
            if (new_left < right and new_right > left and
                new_bottom < top and new_top > bottom):
                return True
        return False

    def on_window_resize(self, window, width, height):
        """Update platform positions and sizes when window is resized."""
        self.spawn_platforms()  # Respawn platforms with new scaling

    def spawn_obstacles(self, dt=None):
        """Spawn one enemy with minimum separation."""
        if not self.spawn_obstacles_enabled:
            return
        min_separation = 150 * (Window.width / self.BASE_WIDTH)  # Scale separation dynamically
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