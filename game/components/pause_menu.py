# pause_menu.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.app import App
from components.game import Game

class PauseMenu(BoxLayout):
    def __init__(self, game_instance, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 50
        self.spacing = 20
        self.game_instance = game_instance
        
        # Title
        self.add_widget(Label(
            text='Paused',
            font_size=48,
            size_hint=(1, 0.4)
        ))
        
        # Resume Button
        self.resume_button = Button(
            text='Resume',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(0, 1, 0, 1)
        )
        self.resume_button.bind(on_press=self.resume_game)
        self.add_widget(self.resume_button)
        
        # Settings Button
        self.settings_button = Button(
            text='Settings',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(0.5, 0.5, 1, 1)
        )
        self.settings_button.bind(on_press=self.show_settings)
        self.add_widget(self.settings_button)
        
        # Exit to Main Menu Button
        self.exit_button = Button(
            text='Exit to Main Menu',
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(1, 0, 0, 1)
        )
        self.exit_button.bind(on_press=self.exit_to_main_menu)
        self.add_widget(self.exit_button)

    def resume_game(self, instance):
        """Resume the current game."""
        self.game_instance.game_active = True
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(self.game_instance)

    def show_settings(self, instance):
        """Show settings popup with volume controls."""
        settings_content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Background Music Volume Slider
        music_label = Label(text='Background Music Volume')
        settings_content.add_widget(music_label)
        
        music_slider = Slider(
            min=0,
            max=1,
            value=self.game_instance.music_manager.current_music.volume if self.game_instance.music_manager.current_music else 1.0,
            step=0.1
        )
        music_slider.bind(value=self.on_music_volume_change)
        settings_content.add_widget(music_slider)
        
        # Sound Effects Volume Slider
        effects_label = Label(text='Sound Effects Volume')
        settings_content.add_widget(effects_label)
        
        effects_slider = Slider(
            min=0,
            max=1,
            value=self.game_instance.music_manager.effects_volume,
            step=0.1
        )
        effects_slider.bind(value=self.on_effects_volume_change)
        settings_content.add_widget(effects_slider)
        
        # Close Button
        close_button = Button(
            text='Close',
            size_hint=(1, 0.3)
        )
        settings_content.add_widget(close_button)
        
        popup = Popup(
            title='Settings',
            content=settings_content,
            size_hint=(0.6, 0.6),
            auto_dismiss=True
        )
        close_button.bind(on_press=lambda x: self.close_popup(popup))
        popup.open()

    def on_music_volume_change(self, instance, value):
        """Adjust background music volume."""
        if self.game_instance.music_manager.current_music:
            self.game_instance.music_manager.current_music.volume = value

    def on_effects_volume_change(self, instance, value):
        """Adjust sound effects volume."""
        self.game_instance.music_manager.set_effects_volume(value)

    def close_popup(self, popup):
        """Close the settings popup without resuming the game."""
        popup.dismiss()

    def exit_to_main_menu(self, instance):
        """Return to the main menu."""
        self.game_instance.music_manager.stop_music()
        app = App.get_running_app()
        app.root.clear_widgets()
        from main import MainMenu
        app.root.add_widget(MainMenu())