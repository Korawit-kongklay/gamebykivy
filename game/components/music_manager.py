from kivy.core.audio import SoundLoader

class MusicManager:
    def __init__(self):
        """Initialize the music manager with audio files."""
        self.background_music = SoundLoader.load('assets/audio/background_music.mp3')
        self.stage_100_music = SoundLoader.load('assets/audio/stage_100_music.mp3')
        self.current_music = None

    def play_music(self, stage_number):
        """Play the appropriate background music based on stage number."""
        if stage_number < 3:
            new_music = self.background_music
        else:
            new_music = self.stage_100_music

        if self.current_music != new_music:
            if self.current_music:
                self.current_music.stop()
            self.current_music = new_music
            if self.current_music:
                self.current_music.loop = True  # Loop the music
                self.current_music.play()
                print(f"Playing music for stage {stage_number}")

    def stop_music(self):
        """Stop the currently playing music."""
        if self.current_music:
            self.current_music.stop()
            self.current_music = None