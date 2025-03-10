from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from components.start_menu import StartMenu
from components.dino_game import DinoGame  # นำเข้า DinoGame จาก dino_game.py

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = DinoGame()
        self.add_widget(self.game)
class DinoApp(App):
    def build(self):
        self.screen_manager = ScreenManager()

        start_menu = StartMenu(name='start')
        self.screen_manager.add_widget(start_menu)

        game_screen = GameScreen(name='game')
        self.screen_manager.add_widget(game_screen)

        return self.screen_manager

if __name__ == '__main__':
    DinoApp().run()