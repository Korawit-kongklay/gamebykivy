from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label

class Dino(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(0, self.velocity_y) + self.pos
        if self.y < 0:
            self.y = 0
            self.velocity_y = 0

class Obstacle(Widget):
    def move(self):
        self.x -= 5

class DinoGame(Widget):
    dino = ObjectProperty(None)
    obstacle = ObjectProperty(None)
    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super(DinoGame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar' and self.dino.y == 0:
            self.dino.velocity_y = 10
        return True

    def update(self, dt):
        if self.dino is None or self.obstacle is None:
            print("Error: Dino or Obstacle not initialized!")
            return
        self.dino.velocity_y -= 0.5
        self.dino.move()
        self.obstacle.move()
        if self.obstacle.x < -self.obstacle.width:
            self.obstacle.x = self.width
            self.score += 1
        if self.dino.collide_widget(self.obstacle):
            self.game_over()

    def game_over(self):
        self.remove_widget(self.obstacle)
        self.add_widget(Label(text=f'Game Over! Score: {self.score}', font_size=40, center=self.center))
        Clock.unschedule(self.update)

class DinoApp(App):
    def build(self):
        game = DinoGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    DinoApp().run()