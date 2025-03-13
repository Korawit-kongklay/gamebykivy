from .enemy import Enemy
from .bullet import BossBullet
from kivy.properties import NumericProperty

class Boss(Enemy):
    health = NumericProperty(3)

    def __init__(self, **kwargs):
        super().__init__(gif_path='assets/gifs/jacko.gif', size=(60, 80), velocity_x=-1, **kwargs)

    def shoot(self, game):
        bullet = BossBullet(start_pos=(self.x - 15, self.y + self.height / 2))
        game.add_widget(bullet)
        game.boss_bullets.append(bullet)