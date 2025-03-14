from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Rotate
from kivy.graphics.texture import Texture
from PIL import Image
import os
from .gif_loader import GifLoader
from .hitbox import Hitbox

class Portal(Widget):
    current_frame = NumericProperty(0)
    texture = ObjectProperty(None)
    textures = ListProperty([])
    frame_count = NumericProperty(0)

    def __init__(self, pos, player=None, gif_path='assets/gifs/portal.gif', size=(80, 240), **kwargs):
        super().__init__(**kwargs)
        self.size = size  # Size set to 80x240
        self.pos = pos
        self.player = player  # Store reference to player for dynamic updates
        self.frame_duration = 0.2  # 200ms per frame
        self.animation_event = None
        self.hitbox = Hitbox(offset_x=0, offset_y=0, width=80, height=240)  # Matches size
        self.rect_instruction = None
        self.rot = None
        # Initial angle based on player's position
        self.angle = 0
        if player:
            self.update_angle()  # Set initial angle
        self.load_animations(gif_path)
        if self.textures:
            self.animation_event = Clock.schedule_interval(self.update_frame, self.frame_duration)
            # Schedule dynamic angle updates
            Clock.schedule_interval(self.update, 1.0 / 60.0)
            print(f"Animation scheduled with interval: {self.frame_duration} seconds")
        else:
            print("No textures loaded, using fallback")
            self.load_fallback()

    def load_animations(self, gif_path: str):
        try:
            print(f"Attempting to load GIF from: {gif_path}")
            frames = GifLoader.load_gif_frames(gif_path)
            if not frames:
                raise ValueError(f"No frames loaded from {gif_path}")
            self.frames = frames
            self.textures = GifLoader.create_textures(frames)
            self.frame_count = len(self.textures)
            if self.textures:
                self.texture = self.textures[0]
                self.update_graphics()
                print(f"Loaded {self.frame_count} frames")
            else:
                raise ValueError("Failed to create textures")
        except Exception as e:
            print(f"Error loading animations: {e}")

    def load_fallback(self):
        with self.canvas:
            Color(0, 1, 1, 1)  # Cyan as fallback
            self.rect_instruction = Rectangle(pos=self.pos, size=self.size)

    def update_angle(self):
        """Update the portal's facing direction based on the player's position."""
        if not self.player:
            return
        player_center_x = self.player.center_x
        portal_center_x = self.center_x
        if player_center_x < portal_center_x:
            self.angle = 180  # Face left
        else:
            self.angle = 0    # Face right

    def update(self, dt: float):
        """Update method to dynamically adjust the portal's orientation."""
        self.update_angle()
        self.update_graphics()

    def update_graphics(self):
        """Update the graphical representation with the current angle."""
        # Clear previous instructions
        if self.rect_instruction:
            self.canvas.remove(self.rect_instruction)
        if self.rot:
            self.canvas.remove(self.rot)

        with self.canvas:
            PushMatrix()
            self.rot = Rotate(angle=self.angle, origin=(self.center_x, self.center_y))
            self.rect_instruction = Rectangle(pos=self.pos, size=self.size, texture=self.texture)
            PopMatrix()

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_frame(self, dt: float):
        """Update the animation frame."""
        if self.frame_count and self.textures and self.rect_instruction:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.texture = self.textures[self.current_frame]
            self.update_graphics()  # Redraw with current rotation
            self.canvas.ask_update()
            print(f"Updated to frame {self.current_frame} at time {Clock.get_time()}")
        else:
            print(f"Cannot update frame: frame_count={self.frame_count}, textures={len(self.textures)}, rect={self.rect_instruction is not None}")

    def update_rect(self, *args):
        """Update the position and size of the rectangle."""
        if self.rect_instruction:
            self.rect_instruction.pos = self.pos
            self.rect_instruction.size = self.size
            if self.rot:
                self.rot.origin = (self.center_x, self.center_y)

    def get_hitbox_rect(self):
        """Return the hitbox rectangle."""
        return self.hitbox.get_rect(self.x, self.y)

    def on_parent(self, instance, parent):
        """Handle removal from parent by canceling scheduled events."""
        if parent is None and self.animation_event:
            self.animation_event.cancel()
            print("Animation event cancelled due to parent removal")