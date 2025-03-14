from kivy.core.audio import SoundLoader
from kivy.clock import Clock

class MusicManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MusicManager, cls).__new__(cls)
            # Initialize audio files only once
            cls._instance.menu_music = SoundLoader.load('assets/audio/menu_music.mp3')
            cls._instance.background_music = SoundLoader.load('assets/audio/background_music.mp3')
            cls._instance.stage_100_music = SoundLoader.load('assets/audio/stage_100_music.mp3')
            cls._instance.current_music = None
            cls._instance.fade_event = None

            # Sound effects
            cls._instance.walk_sound = SoundLoader.load('assets/audio/walk.mp3')
            cls._instance.shoot_sound = SoundLoader.load('assets/audio/shoot.mp3')
            cls._instance.jump_sound = SoundLoader.load('assets/audio/jump.mp3')
            cls._instance.spawn_sound = SoundLoader.load('assets/audio/spawn.mp3')
            cls._instance.die_sound = SoundLoader.load('assets/audio/die.mp3')
            
            # Default volumes
            cls._instance.effects_volume = 1.0
            cls._instance.music_volume = 0.1  # เพิ่มตัวแปรเก็บ volume ของเพลง
            cls._instance.set_effects_volume(cls._instance.effects_volume)
        return cls._instance

    def play_menu_music(self):
        """Play the menu background music."""
        if self.current_music:
            self.current_music.stop()
        self.current_music = self.menu_music
        if self.current_music:
            self.current_music.volume = self.music_volume
            self.current_music.loop = True
            self.current_music.play()
            print("Playing menu music")

    def play_music(self, stage_number):
        """Play the appropriate background music based on stage number."""
        if stage_number < 5:
            new_music = self.background_music
        else:
            new_music = self.stage_100_music

        if self.current_music != new_music:
            if self.current_music:
                self.current_music.stop()
            self.current_music = new_music
            if self.current_music:
                self.current_music.volume = self.music_volume
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

    def set_music_volume(self, volume):
        """Set the volume for background music."""
        self.music_volume = volume
        if self.current_music:
            self.current_music.volume = volume

    def set_effects_volume(self, volume):
        """Set the volume for all sound effects."""
        self.effects_volume = volume
        if self.walk_sound:
            self.walk_sound.volume = volume * 0.5
        if self.shoot_sound:
            self.shoot_sound.volume = volume * 0.7
        if self.jump_sound:
            self.jump_sound.volume = volume * 0.6
        if self.spawn_sound:
            self.spawn_sound.volume = volume * 0.5
        if self.die_sound:
            self.die_sound.volume = volume * 0.8

    # Sound effect methods
    def play_walk(self):
        if self.walk_sound:
            self.walk_sound.play()

    def play_shoot(self):
        if self.shoot_sound:
            self.shoot_sound.play()

    def play_jump(self):
        if self.jump_sound:
            self.jump_sound.play()

    def play_spawn(self):
        if self.spawn_sound:
            self.spawn_sound.play()

    def play_die(self):
        if self.die_sound:
            self.die_sound.play()