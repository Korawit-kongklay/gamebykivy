# stage.py (full updated version)
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
import random
from .obstacle import Obstacle
from .platform import Platform
#from .powerup import SpeedPowerUp, ShieldPowerUp, AmmoPowerUp, HealthPowerUp, ScorePowerUp

class Stage(Widget):
    stage_number = NumericProperty(1)
    obstacles_to_clear = NumericProperty(10)
    obstacles_cleared = NumericProperty(0)
    obstacles = []
    power_ups = []
    platforms = []

    def __init__(self, stage_number=1, **kwargs):
        super().__init__(**kwargs)
        self.stage_number = stage_number
        self.obstacles_to_clear = 10 + (stage_number - 1) * 5
        self.spawn_platforms()
        self.bind(size=self._check_size_and_spawn)  # Bind to size changes
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def _check_size_and_spawn(self, instance, value):
        """Spawn obstacles once size is valid."""
        if self.height >= 100:  # Ensure height is reasonable (e.g., > obstacle.height + 50)
            self.unbind(size=self._check_size_and_spawn)  # Unbind after spawning
            self.spawn_obstacles()

    def spawn_platforms(self):
        if self.stage_number == 1:
            platform_positions = [
                (0, 0, 800, 50),
                (200, 150, 200, 30),
                (450, 250, 150, 30),
                (100, 350, 180, 30),
            ]
        elif self.stage_number == 2:
            platform_positions = [
                (0, 0, 600, 50),
                (150, 100, 150, 30),
                (400, 200, 200, 30),
                (300, 350, 180, 30),
                (600, 300, 150, 30),
            ]
        else:
            platform_positions = [
                (0, 0, 800, 50),
                (random.randint(100, 600), random.randint(100, 400), 200, 30),
            ]

        for x, y, width, height in platform_positions:
            platform = Platform(pos=(x, y), size=(width, height))
            self.add_widget(platform)
            self.platforms.append(platform)

    def spawn_obstacles(self):
        for _ in range(self.obstacles_to_clear):
            obstacle = Obstacle()
            obstacle.x = self.width + random.randint(0, 300)
            obstacle.y = random.randint(50, max(50, self.height - obstacle.height))
            self.add_widget(obstacle)
            self.obstacles.append(obstacle)

#    def spawn_power_up(self):
#        spawn_chance = 0.01 if self.stage_number == 1 else 0.015
#        if random.random() < spawn_chance:
#            power_up_types = [SpeedPowerUp, ShieldPowerUp, AmmoPowerUp, HealthPowerUp, ScorePowerUp]
#            power_up = random.choice(power_up_types)()
#            power_up.x = self.width + random.randint(0, 300)
#            power_up.y = random.randint(50, max(50, self.height - power_up.height))
#            self.add_widget(power_up)
#            self.power_ups.append(power_up)
            
    def update(self, dt):
        for obstacle in self.obstacles[:]:
            obstacle.move()
            on_platform = False
            for platform in self.platforms:
                if (obstacle.collide_widget(platform) and 
                    obstacle.y > platform.y and 
                    obstacle.bottom <= platform.top + 5):
                    obstacle.y = platform.top
                    obstacle.velocity_y = 0
                    on_platform = True
                    break
            if not on_platform and obstacle.y <= 0:
                obstacle.y = 0
                obstacle.velocity_y = 0
            if obstacle.x < -obstacle.width:
                self.remove_widget(obstacle)
                self.obstacles.remove(obstacle)
                self.obstacles_cleared += 1

        for power_up in self.power_ups[:]:
            if power_up.x < -power_up.width:
                self.remove_widget(power_up)
                self.power_ups.remove(power_up)

#        self.spawn_power_up()

        if self.obstacles_cleared >= self.obstacles_to_clear:
            self.next_stage()

    def next_stage(self):
        self.stage_number += 1
        self.obstacles_cleared = 0
        self.obstacles.clear()
        self.power_ups.clear()
        self.spawn_platforms()
        self.spawn_obstacles()