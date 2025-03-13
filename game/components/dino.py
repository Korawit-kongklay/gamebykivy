from .player import Character

class Dino(Character):
    def __init__(self, **kwargs):
        super().__init__(gif_path='assets/gifs/ufopug.gif', **kwargs)