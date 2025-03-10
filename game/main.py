from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from components.dino_game import DinoGame  # Import DinoGame from dino_game.py
from components.start_menu import StartMenu
from components.setting_menu import SettingsMenu
from components.pause_menu import PauseMenu
from components.gameover_menu import GameOverMenu

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = DinoGame()
        self.add_widget(self.game)

class DinoApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Create screens
        start_menu = StartMenu(name='start')
        settings_menu = SettingsMenu(name='settings')
        pause_menu = PauseMenu(name='pause')
        game_over_menu = GameOverMenu(name='game_over')
        game_screen = GameScreen(name='game')  # Add the GameScreen
        
        # Add screens to the ScreenManager
        sm.add_widget(start_menu)
        sm.add_widget(settings_menu)
        sm.add_widget(pause_menu)
        sm.add_widget(game_over_menu)
        sm.add_widget(game_screen)  # Add the GameScreen to the ScreenManager
        
        return sm

if __name__ == '__main__':
    DinoApp().run()