from .obstacle import Obstacle
from .bullet import Bullet
from kivy.properties import NumericProperty

class BossBullet(Bullet):
    def __init__(self, **kwargs):
        super().__init__(start_pos=(0, 0), target_pos=(-1, 0), speed=5, **kwargs)

    def move(self) -> None:
        self.x -= 5  # Fixed speed to left

class Boss(Obstacle):
    health = NumericProperty(3)

    def __init__(self, **kwargs):
        super().__init__(velocity_x=-1, **kwargs)  # Slower than regular enemies

    def shoot(self, game) -> None:
        bullet = BossBullet()
        bullet.pos = (self.x - bullet.width, self.y + self.height / 2)
        game.add_widget(bullet)
        game.boss_bullets.append(bullet)