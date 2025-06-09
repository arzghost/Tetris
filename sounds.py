import pygame

class SoundEffects:
    def __init__(self):
        pygame.mixer.init()
        
        # Create simple sounds using pygame.mixer.Sound.play()
        self.move_sound = self._create_move_sound()
        self.rotate_sound = self._create_rotate_sound()
        self.clear_sound = self._create_clear_sound()
        self.drop_sound = self._create_drop_sound()
        
    def _create_move_sound(self):
        sound = pygame.mixer.Sound(buffer=self._generate_sound_buffer(440, 50))
        sound.set_volume(0.2)
        return sound

    def _create_rotate_sound(self):
        sound = pygame.mixer.Sound(buffer=self._generate_sound_buffer(550, 50))
        sound.set_volume(0.2)
        return sound

    def _create_clear_sound(self):
        sound = pygame.mixer.Sound(buffer=self._generate_sound_buffer(660, 200))
        sound.set_volume(0.3)
        return sound

    def _create_drop_sound(self):
        sound = pygame.mixer.Sound(buffer=self._generate_sound_buffer(330, 100))
        sound.set_volume(0.25)
        return sound

    def _generate_sound_buffer(self, frequency, duration):
        """Generate a simple sine wave sound"""
        import numpy as np
        sample_rate = 44100
        t = np.linspace(0, duration/1000, int(sample_rate * duration/1000))
        samples = np.sin(2 * np.pi * frequency * t)
        # Apply fade out
        fade = np.linspace(1, 0, len(samples))
        samples = samples * fade
        return (samples * 32767).astype(np.int16).tobytes()

    def play_move(self):
        self.move_sound.play()

    def play_rotate(self):
        self.rotate_sound.play()

    def play_clear(self):
        self.clear_sound.play()

    def play_drop(self):
        self.drop_sound.play()
