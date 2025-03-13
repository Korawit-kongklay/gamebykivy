from kivy.config import Config
Config.set('graphics', 'width', '1280')  # Full HD width
Config.set('graphics', 'height', '720')  # Full HD height
from kivy.app import App
from components.dino_game import DinoGame

class DinoApp(App):
    def build(self):
        return DinoGame()

if __name__ == '__main__':
    DinoApp().run()