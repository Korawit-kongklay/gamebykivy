from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder

# Load the KV file
Builder.load_file("game.kv")

class GameScreen(Screen):
    def on_enter(self):
        print("GameScreen loaded!")

class RiskGame(App):
    def build(self):
        print("Starting Game...")
        sm = ScreenManager()
        sm.add_widget(GameScreen(name="game"))
        return sm

if __name__ == "__main__":
    RiskGame().run()
    print("Game Ended")