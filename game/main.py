from kivy.app import App
from kivy.clock import Clock
from components.dino_game import DinoGame  # นำเข้า DinoGame จาก dino_game.py

class DinoApp(App):
    def build(self):
        game = DinoGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    DinoApp().run()