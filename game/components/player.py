from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Line, Color, Rectangle
from .gif_loader import GifLoader
from .hitbox import Hitbox


class Character(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    texture = ObjectProperty(None)
    facing_right = BooleanProperty(True)
    hitbox = ObjectProperty(None)

    def __init__(self, gif_path: str, size: tuple = (80, 80), **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.hitbox = Hitbox(offset_x=10, offset_y=0, width=size[0]-20, height=size[1])
        self.debug_hitbox_visible = False
        self.debug_hitbox_instruction = None
        self.rect_instruction = None  # Store the rectangle instruction for the character
        try:
            self.load_animations(gif_path)
            Clock.schedule_interval(self.update_frame, 0.1)
        except Exception as e:
            print(f"Failed to load animations from {gif_path}: {e}")
            # Fallback to a solid color rectangle if GIF loading fails
            self.texture = None
            self.load_fallback()
        self.update_graphics()

    def load_animations(self, gif_path: str):
        """Load GIF frames and create textures for animation."""
        self.frames = GifLoader.load_gif_frames(gif_path)
        if not self.frames:
            raise ValueError(f"No frames loaded from {gif_path}")
        self.current_frame = 0
        self.frame_count = len(self.frames)
        self.original_frames = GifLoader.create_textures(self.frames)
        self.flipped_frames = GifLoader.create_flipped_textures(self.frames)
        if not self.original_frames or not self.flipped_frames:
            raise ValueError("Failed to create textures from GIF frames")
        self.texture = self.original_frames[0]

    def load_fallback(self):
        """Load a fallback solid color if GIF loading fails."""
        with self.canvas:
            Color(1, 0, 0, 1)  # Fallback to red for visibility
            self.rect_instruction = Rectangle(pos=self.pos, size=self.size)

    def update_graphics(self):
        """Initialize or update the character's graphics on the canvas."""
        if self.rect_instruction:
            self.canvas.remove(self.rect_instruction)
        with self.canvas:
            # Ensure no unintended color tint
            Color(1, 1, 1, 1)  # White color to avoid tinting the texture
            self.rect_instruction = Rectangle(pos=self.pos, size=self.size, texture=self.texture)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_frame(self, dt: float):
        """Update the current animation frame."""
        if not self.frame_count or not self.original_frames:
            return
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.texture = self.original_frames[self.current_frame] if self.facing_right else self.flipped_frames[self.current_frame]
        self.update_graphics()
        self.canvas.ask_update()

    def move(self):
        """Move the character based on velocity."""
        self.pos = Vector(*self.velocity) + self.pos
        self.x = max(0, min(self.x, Window.width - self.width))

    def on_velocity_x(self, instance, value: float):
        """Update facing direction based on velocity."""
        self.facing_right = value >= 0

    def get_hitbox_rect(self):
        """Get the hitbox rectangle for collision detection."""
        return self.hitbox.get_rect(self.x, self.y)

    def toggle_hitbox_debug(self, visible: bool):
        """Show or hide the hitbox debug outline."""
        self.debug_hitbox_visible = visible
        if visible:
            self.update_hitbox_debug()
        else:
            if self.debug_hitbox_instruction:
                self.canvas.after.remove(self.debug_hitbox_instruction)
                self.debug_hitbox_instruction = None

    def update_hitbox_debug(self):
        """Update the hitbox debug outline position and size."""
        if not self.debug_hitbox_visible:
            return
        hitbox_rect = self.get_hitbox_rect()
        if self.debug_hitbox_instruction:
            self.canvas.after.remove(self.debug_hitbox_instruction)
        with self.canvas.after:
            Color(1, 0, 0, 1)  # Red outline for player
            self.debug_hitbox_instruction = Line(
                rectangle=(
                    hitbox_rect['x'], hitbox_rect['y'],
                    hitbox_rect['width'], hitbox_rect['height']
                ),
                width=1
            )

    def update_rect(self, *args):
        """Update the rectangle position and size when the widget moves."""
        if self.rect_instruction:
            self.rect_instruction.pos = self.pos
            self.rect_instruction.size = self.size


class Player(Character):
    def __init__(self, **kwargs):
        super().__init__(gif_path='assets/gifs/ufopug.gif', **kwargs)