import asyncio
import edge_tts
import pygame
import os
import uuid
import threading
import shutil
import atexit
import random
import json
#import ai_core.brain import LocalBrain
from config_manager import save_last_pet, load_last_pet


# ===========================================
# 🗂️ TEMP FOLDER SETUP
# ===========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "Voices")

if os.path.exists(TEMP_DIR):
    try:
        shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR, exist_ok=True)
        print("🧼 Cleaned up old temp voice files at startup.")
    except Exception as e:
        print("⚠️ Startup cleanup failed:", e)

os.makedirs(TEMP_DIR, exist_ok=True)
print(f"Temp voice folder Ready: {TEMP_DIR}")
# ===========================================
# 🧹 CLEANUP ON EXIT
# ===========================================
@atexit.register
def cleanup_temp_audio():
    """Deleted Clippy’s temporary audio folder when program closes."""
    import pygame, time
    try:
        if pygame.mixer.get_init():
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            pygame.mixer.quit()
        
        
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
            print("🧹 Deleted local cvoice files")
    except Exception as e:
        print("⚠️ Cleanup Error", e)


def _run_speak_async_in_thread(speak_async_func, text): 
    """Safely runs the async speak function in a new event loop."""
    
    try:
        asyncio.run(speak_async_func(text))
    except Exception as e:
        print(f"Speech thread error: {e}")
# ===========================================
#   PERSONALITY CLASS
# ===========================================
class Personality:
    def __init__(self, path):
        self.path = path
        self.data = self.load_personality()
        
        # pick a deep voice from available ones (change it later)
        self.voice = "en-US-GuyNeural" 
        self.rate = "-20%"              
        self.volume = "+0%"
        
        #Initialize pygame mixer once
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        #Store it 
        self._last_voice_file = None
        
        #Main brain
        #self.brain = LocalBrain("llama3")



    # ===========================================
    #   LOAD PERSONALITY DATA
    # ===========================================
    def load_personality(self):
        if not os.path.exists(self.path):
            print("⚠️ Personality file missing:", self.path)
            return {"name": "Unknown", "idle_messages": [], "mood_reactions": {}}
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)


    # ===========================================
    #   TTS system
    # ===========================================
    async def speak_async(self, text):
        """Generate speech to a unique file, then play it safely."""
        # use unique file each time to avoid permission issues
        out_path = os.path.join(TEMP_DIR, f"temp_SAM_voice_{uuid.uuid4().hex}.mp3")

        communicator = edge_tts.Communicate(
            text, voice=self.voice, rate=self.rate, volume=self.volume
        )
        await communicator.save(out_path)
        
        #stop any voice playing currently
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        #paly the new clip
        pygame.mixer.music.load(out_path)
        pygame.mixer.music.play()
        
        #wait untill done
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        self._last_voice_file = out_path

    # ===========================================
    #   MOOD & IDLE SPEECH
    # ===========================================
    def say_random_idle(self):
        if not self.data["idle_messages"]:
            return
            
        if pygame.mixer.music.get_busy():
            return
            
        # FIX: Use a random choice from the predefined list
        msg = random.choice(self.data["idle_messages"])
        
        # Add safety check against empty/single-character text
        if not msg or len(msg.strip()) < 3:
            print(f"⚠️ Skipping idle speech: Message is too short/empty: '{msg}'")
            return
            
        print(f"{self.data['name']}: {msg}")
        # --- FIX: Launch speech in a new thread ---
        threading.Thread(
            target=_run_speak_async_in_thread,
            args=(self.speak_async, msg)
        ).start()

    def say_for_mood(self, mood):
        # FIX: Retrieve the text directly from the mood_reactions dictionary
        text = self.data["mood_reactions"].get(mood)
        
        if pygame.mixer.music.get_busy():
            return
        
        if text and isinstance(text, str):
            # Add safety check against empty/single-character text
            if len(text.strip()) < 3:
                print(f"⚠️ Skipping mood speech ({mood}): Message is too short/empty: '{text}'")
                return
                
            print(f"{self.data['name']} ({mood}): {text}")

            # --- FIX: Launch speech in a new thread ---
            threading.Thread(
                target=_run_speak_async_in_thread,
                args=(self.speak_async, text)
            ).start()
            # ------------------------------------------
        else:
            print(f"{self.data['name']} ({mood}): No valid reaction message found for mood '{mood}'.")