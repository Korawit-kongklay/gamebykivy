from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.clock import Clock
import random
from .platform import Platform
from .obstacle import Obstacle
from kivy.core.window import Window

class Stage(Widget):
    stage_number = NumericProperty(1)
    obstacles = []
    platforms = []

    def __init__(self, stage_number=1, spawn_obstacles=False, **kwargs):
        super().__init__(**kwargs)
        self.stage_number = stage_number
        self.spawn_obstacles_enabled = spawn_obstacles
        self.spawn_platforms()
        if self.spawn_obstacles_enabled:
            Clock.schedule_once(self.spawn_obstacles, 0.1)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def spawn_platforms(self):
        # Scale factors from original 800x600 to 1920x1080
        base_width, base_height = 800, 600
        width_scale = Window.width / base_width  # 1920 / 800 = 2.4
        height_scale = Window.height / base_height  # 1080 / 600 = 1.8

        platform_configs = {
            1: [(200, 150), (293, 150), (386, 150),(450, 250), (543, 250),(100, 350), (193, 350), (286, 350)],
            2: [(150, 100), (400, 200), (300, 350), (600, 300)]
        }.get(self.stage_number, [
            (random.randint(0, Window.width - 15), random.randint(0, Window.height - 8)),
            (random.randint(0, Window.width - 15), random.randint(0, Window.height - 8)),
            (random.randint(0, Window.width - 15), random.randint(0, Window.height - 8))  # Added one more for larger screen
        ])

        self.platforms.clear()
        for x, y in platform_configs:
            # Scale fixed positions for Stages 1 and 2
            if (x, y) in [(200, 150), (450, 250), (100, 350), (150, 100), (400, 200), (300, 350), (600, 300)]:
                x = int(x * width_scale)  # e.g., 200 * 2.4 = 480
                y = int(y * height_scale)  # e.g., 150 * 1.8 = 270
            platform = Platform(pos=(x, y), size=(93, 24))  # Keeping size (15, 8) for now
            self.add_widget(platform)
            self.platforms.append(platform)

    def spawn_obstacles(self, dt=None):
        if not self.spawn_obstacles_enabled:
            return
        for _ in range(5):
            obstacle = Obstacle()
            obstacle.x = Window.width + random.randint(0, 300)  # Starts off-screen at 1920+
            obstacle.y = random.randint(50, max(50, Window.height - obstacle.height))  # Up to 1080
            self.add_widget(obstacle)
            self.obstacles.append(obstacle)

    def update(self, dt):
        if not self.spawn_obstacles_enabled:
            return
        for obstacle in self.obstacles[:]:
            obstacle.move()
            on_platform = self.check_platform_collision(obstacle)
            if not on_platform and obstacle.y <= 0:
                obstacle.y = 0
                obstacle.velocity_y = 0
            if obstacle.x < -obstacle.width:
                self.remove_widget(obstacle)
                self.obstacles.remove(obstacle)

    def check_platform_collision(self, obstacle):
        for platform in self.platforms:
            if (obstacle.collide_widget(platform) and 
                obstacle.y > platform.y and 
                obstacle.y <= platform.top + 5):
                obstacle.y = platform.top
                obstacle.velocity_y = 0
                return True
        return False