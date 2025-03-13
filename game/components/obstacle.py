from .enemy import Enemy

class Obstacle(Enemy):
    def __init__(self, **kwargs):
        super().__init__(size=(50, 50), **kwargs)