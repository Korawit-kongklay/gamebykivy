# music_manager.py
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

class MusicManager:
    def __init__(self):
        """Initialize the music manager with audio files."""
        self.background_music = SoundLoader.load('assets/audio/background_music.mp3')
        self.stage_100_music = SoundLoader.load('assets/audio/stage_100_music.mp3')
        self.current_music = None
        self.fade_event = None  # To store the scheduled fade event

    def play_music(self, stage_number):
        """Play the appropriate background music based on stage number."""
        if stage_number < 100:
            new_music = self.background_music
        else:
            new_music = self.stage_100_music

        if self.current_music != new_music:
            if self.current_music:
                self.current_music.stop()
            self.current_music = new_music
            if self.current_music:
                self.current_music.volume = 1.0  # Reset volume to full
                self.current_music.loop = True  # Loop the music
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
        
        # Cancel any existing fade event
        if self.fade_event:
            self.fade_event.cancel()

        # Calculate the volume step per frame (assuming 60 FPS)
        initial_volume = self.current_music.volume
        step = initial_volume / (duration * 60)  # Volume decrease per frame

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

        # Schedule the fade-out updates
        self.fade_event = Clock.schedule_interval(_fade, 1.0 / 60.0)