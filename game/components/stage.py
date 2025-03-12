from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
import random
from .obstacle import Obstacle
from .platform import Platform
from .powerup import SpeedPowerUp, ShieldPowerUp, AmmoPowerUp, HealthPowerUp, ScorePowerUp

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
        self.obstacles_to_clear = 10 + (stage_number - 1) * 5  # Increase difficulty with each stage
        self.spawn_platforms()
        self.spawn_obstacles()
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def spawn_platforms(self):
        # Example: Add a single platform at the bottom
        platform = Platform()
        self.add_widget(platform)
        self.platforms.append(platform)

    def spawn_obstacles(self):
        for _ in range(self.obstacles_to_clear):
            obstacle = Obstacle()
            obstacle.x = random.randint(0, self.width)
            obstacle.y = random.randint(50, self.height - 50)
            self.add_widget(obstacle)
            self.obstacles.append(obstacle)

    def spawn_power_up(self):
        if random.random() < 0.01:  # 1% chance per frame
            power_up_types = [SpeedPowerUp, ShieldPowerUp, AmmoPowerUp, HealthPowerUp, ScorePowerUp]
            power_up = random.choice(power_up_types)()
            power_up.x = random.randint(0, self.width)
            power_up.y = random.randint(50, self.height - 50)
            self.add_widget(power_up)
            self.power_ups.append(power_up)

    def update(self, dt):
        for obstacle in self.obstacles[:]:
            obstacle.move()
            if obstacle.x < -obstacle.width:
                self.remove_widget(obstacle)
                self.obstacles.remove(obstacle)
                self.obstacles_cleared += 1

        for power_up in self.power_ups[:]:
            if power_up.x < -power_up.width:
                self.remove_widget(power_up)
                self.power_ups.remove(power_up)

        self.spawn_power_up()

        if self.obstacles_cleared >= self.obstacles_to_clear:
            self.next_stage()

    def next_stage(self):
        self.stage_number += 1
        self.obstacles_cleared = 0
        self.obstacles.clear()
        self.power_ups.clear()
        self.spawn_obstacles()