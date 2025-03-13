# music_manager.py
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

class MusicManager:
    def __init__(self):
        """Initialize the music manager with audio files."""
        # Background music
        self.background_music = SoundLoader.load('assets/audio/background_music.mp3')
        self.stage_100_music = SoundLoader.load('assets/audio/stage_100_music.mp3')
        self.current_music = None
        self.fade_event = None

        # Sound effects
        self.walk_sound = SoundLoader.load('assets/audio/walk.mp3')
        self.shoot_sound = SoundLoader.load('assets/audio/shoot.mp3')
        self.jump_sound = SoundLoader.load('assets/audio/jump.mp3')
        self.spawn_sound = SoundLoader.load('assets/audio/spawn.mp3')
        self.die_sound = SoundLoader.load('assets/audio/die.mp3')

    def play_music(self, stage_number):
        """Play the appropriate background music based on stage number."""
        if stage_number < 3:  # Keeping your updated threshold of 3
            new_music = self.background_music
        else:
            new_music = self.stage_100_music

        if self.current_music != new_music:
            if self.current_music:
                self.current_music.stop()
            self.current_music = new_music
            if self.current_music:
                self.current_music.volume = 1.0
                self.current_music.loop = True
                self.current_music.play()
                print(f"Playing music for stage {stage_number}")

    def stop_music(self):
        """Stop the currently playing music immediately."""
        if self.current_music:
            self.current_music.stop()
            self.current_music = None
        if self.fade_event:
            self.fade_event.cancel()
            self.fade_event = None

    def fade_out_music(self, duration=1.0):
        """Fade out the current music over the specified duration (in seconds)."""
        if not self.current_music or self.current_music.state != 'play':
            return
        
        if self.fade_event:
            self.fade_event.cancel()

        initial_volume = self.current_music.volume
        step = initial_volume / (duration * 60)

        def _fade(dt):
            if self.current_music and self.current_music.state == 'play':
                self.current_music.volume -= step
                if self.current_music.volume <= 0:
                    self.current_music.volume = 0
                    self.current_music.stop()
                    self.current_music = None
                    if self.fade_event:
                        self.fade_event.cancel()
                        self.fade_event = None
            else:
                if self.fade_event:
                    self.fade_event.cancel()
                    self.fade_event = None

        self.fade_event = Clock.schedule_interval(_fade, 1.0 / 60.0)

    # Sound effect methods
    def play_walk(self):
        """Play the walking sound effect."""
        if self.walk_sound:
            self.walk_sound.volume = 0.5  # Adjust volume if needed
            self.walk_sound.play()

    def play_shoot(self):
        """Play the shooting sound effect."""
        if self.shoot_sound:
            self.shoot_sound.volume = 0.7
            self.shoot_sound.play()

    def play_jump(self):
        """Play the jumping sound effect."""
        if self.jump_sound:
            self.jump_sound.volume = 0.6
            self.jump_sound.play()

    def play_spawn(self):
        """Play the spawning sound effect."""
        if self.spawn_sound:
            self.spawn_sound.volume = 0.5
            self.spawn_sound.play()

    def play_die(self):
        """Play the dying sound effect."""
        if self.die_sound:
            self.die_sound.volume = 0.8
            self.die_sound.play()