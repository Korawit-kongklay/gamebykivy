from .enemy import Enemy
from kivy.properties import NumericProperty

class Boss(Enemy):
    health = NumericProperty(3)

    def __init__(self, **kwargs):
        super().__init__(gif_path='assets/gifs/jacko.gif', size=(60, 80), velocity_x=-1, **kwargs)

    def shoot(self, game):
        from .attack import EnemyProjectile
        attack = EnemyProjectile(start_pos=(self.x - 15, self.y + self.height / 2))
        game.add_widget(attack)
        game.enemy_attacks.append(attack)