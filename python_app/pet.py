import pygame
import random
import os
import time
from PIL import Image
import pygame.mixer
from Clippy_Personality import Personality


class Pet(pygame.sprite.Sprite):
    def __init__(self, image_path, screen_size):
        super().__init__()

        # === Basic setup ===
        self.pet_folder = os.path.dirname(image_path)
        self.personality_path = os.path.join(self.pet_folder, "personality.json")
        
        base_dir = os.path.abspath(os.path.join(self.pet_folder, '..', '..'))
        config_path = os.path.join(base_dir, "config.json")
        
        self.personality = Personality(self.personality_path, config_path=config_path)
        # === Animation frames ===
        self.frames = self.load_gif_frames(image_path)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.screen_w, self.screen_h = screen_size
        self.vx = random.choice([-3, 3])
        self.vy = random.choice([-2, 2])
        self.color = (255, 255, 255)
        self.mood = "idle"
        self.last_mood = None
        self.frame_timer = 0

        # === Music & sounds ===
        self.music_path = self.find_music()
        self.play_music()
        self.sounds = self.load_sounds()

        # === Idle speech timing ===
        self.last_speech_time = 0
        self.speech_cooldown = 10  


    # ===============================
    # 🧩 ASSET LOADERS
    # ===============================
    def load_gif_frames(self, path):
        """Load all frames from an animated GIF."""
        pil_img = Image.open(path)
        frames = []
        for frame in range(pil_img.n_frames):
            pil_img.seek(frame)
            frame_surface = pygame.image.fromstring(
                pil_img.convert("RGBA").tobytes(),
                pil_img.size,
                "RGBA"
            )
            frame_surface = pygame.transform.scale(frame_surface, (200, 200))
            frames.append(frame_surface)
        return frames

    def find_music(self):
        """Find a background music file inside the pet folder."""
        music_dir = os.path.join(self.pet_folder, "Sounds")
        if not os.path.exists(music_dir):
            return None
        for file in os.listdir(music_dir):
            if file.endswith((".mp3", ".wav", ".ogg")):
                return os.path.join(music_dir, file)
        return None

    def play_music(self):
        """Play background music if available."""
        if self.music_path:
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)

    def load_sounds(self):
        """Load mood-specific sound effects."""
        sound_dir = os.path.join(self.pet_folder, "sounds")
        sounds = {}
        if not os.path.exists(sound_dir):
            return sounds
        for mood in ["overheated", "warm", "low-battery", "cooling", "happy", "idle"]:
            file_path = os.path.join(sound_dir, f"{mood}.mp3")
            if os.path.exists(file_path):
                sounds[mood] = pygame.mixer.Sound(file_path)
        return sounds

    def play_mood_sound(self, mood):
        """Play a sound associated with a mood."""
        if mood in self.sounds:
            pygame.mixer.stop()
            self.sounds[mood].play()


    # ===============================
    # 🧩 MAIN UPDATE LOOP
    # ===============================
    def update_from_mood(self, mood):
        """Sets the mood and color tinting."""
        self.mood = mood
        
        mood_colors = {
            "MELTING": (255, 50, 50),
            "GAMING_HARD": (200, 0, 255),
            "PANICKED": (255, 140, 0),
            "STUFFED": (100, 255, 100),
            "BORED": (150, 150, 255),
            "CHILLING": (255, 255, 255),
        }
        
        self.color = mood_colors.get(self.mood, (255, 255, 255))

        if self.mood != self.last_mood:
            if hasattr(self, "personality"):
                self.personality.say_for_mood(self.mood)
                self.play_mood_sound(self.mood)
            self.last_mood = self.mood

    def update(self):
        """Handles movement and animation frames."""
        # --- Movement ---
        self.rect.x += self.vx
        self.rect.y += self.vy

        if self.rect.left < 0 or self.rect.right > self.screen_w:
            self.vx *= -1
        if self.rect.top < 0 or self.rect.bottom > self.screen_h:
            self.vy *= -1

        # --- Frame Animation ---
        self.frame_timer += 1
        if self.frame_timer % 2 == 0:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

        # --- Occasional idle chatter ---
        current_time = time.time()
        if current_time - self.last_speech_time > self.speech_cooldown:
            if random.randint(0, 100) == 1:
                self.personality.say_random_idle()
                self.last_speech_time = current_time


    # ===============================
    # 🧩 DRAW
    # ===============================
    def draw(self, screen):
        tinted = self.image.copy()
        tint_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        tint_surface.fill((*self.color, 60))
        tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(tinted, self.rect)
