import asyncio
import time
import pygame
import os
import uuid
import threading
#import tempfile
import shutil
import atexit
import random
import json

import edge_tts
from edge_tts.exceptions import NoAudioReceived


try:
    from ai_core.brain import OpenAIBrain, LocalBrain, AIBrain
except ImportError:
    class AIBrain:
        def ask(self, prompt, context): 
            return "Sorry, i wasn't loaded correctly (ImportError)."
    OpenAIBrain = AIBrain
    LocalBrain = AIBrain
    print("Error: ai_core/brain.py AI wasnt found.\nCurrently using placeholders")    

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
        
        
# ===============================
#    AI Brain Initialization
# ===============================        
def get_ai_brain(config_path):
    """Initiates the AI brain based on Config"""
    try: 
        with open(config_path, "r") as f:
            full_config = json.load(f)
            ai_config = full_config.get("ai_config", {"enabled": False})
    except Exception: 
        ai_config = {"enabled": False}
    
    if not ai_config.get("enabled", False):
        print(" AI disabeled in Config.json")
        return None
    
    backend = ai_config.get("backend", "local").lower()
    
    try: 
        if backend == "openai":
            return OpenAIBrain()
        elif backend == "local":
            return LocalBrain()
        else:
            print(f"Unknown AI backend '{backend}'. Using LocalBrain placeholder")
            return LocalBrain()
    except Exception as e:
        print(f"Failed to int AI Brain({backend}): {e}")
        
    
# ======================
#   PERSONALITY CLASS
# ======================
class Personality:
    def __init__(self, personality_path: str, config_path: str):
        self.personality_path = personality_path 
        self.data = self._load_data(personality_path)
        
        # pick a deep voice from available ones (change it later)
        self.voice = "en-US-ChristopherNeural" 
        self.rate = "+0%"              
        self.volume = "+0%"
        self.name = self.data.get("name", "Pet")
        
        self.brain: AIBrain | None = get_ai_brain(config_path)
        self._last_voice_file = None
        
        #Initialize pygame mixer once
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        #Store it 
        self._last_voice_file = None
        
        #holds the text to show in the bubble and for how long to show that bubble for 0 for forever
        self.current_text = None
        self.display_timer = 0
        
        #gotta prevent him from screeming every 1 seccond
        self.last_mood_shout = 0


    # ============================================================
    #   Testing the bubble (Not important just here for testng)
    # ============================================================
    def text_bubble(self, message="I am Working"):
        """Manually forcingt he text into the bubble"""
        self.current_text = message
        self.display_timer = time.time() + 5
        print(f"DEBUG: bubble text set to {message}")
    
    # =========================
    #   LOAD personality DATA
    # =========================
    def _load_data(self, path: str): 
        if not os.path.exists(path):
            print("⚠️ personality file missing:", path)
            return {"name": "Unknown", "idle_messages": [], "mood_reactions": {}}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
            
            
    def update_mood_from_stats(self, stats):
        cpu = stats.get("cpu_usage", 0)
        gpu = stats.get("gpu_usage", 0)
        temp = stats.get("gpu_temp", 0)
        mem = stats.get("mem_usage", 0) 
        
        if temp > 85:
            return "MELTING"
        elif mem > 90:             
            return "STUFFED"
        elif gpu > 90:
            return "GAMING_HARD"
        elif cpu < 5:
            return "BORED"
        else:
            return "CHILLING"
    
    
    # ===============
    #   TTS system
    # ===============
    async def speak_async(self, text):
        """Generate speech to a unique file, then play it safely."""
        # use unique file each time to avoid perission issues
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


    # ========================
    #   async speach wrapper
    # ========================
    def _run_speech_sync(self, msg):
        """Blocking call to sep to gene tts"""
        MAX_RETRIES = 3
        RETRY_DELAY = 2
        
        for attempt in range(MAX_RETRIES):
            try: 
                asyncio.run(self.speak_async(msg))
                return
            except NoAudioReceived as e:
                print(f"[TTS ERROR] no audio detected. Try {attempt + 1}/{MAX_RETRIES}. ERROR: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    print("[TTS FATAL]: Tough Luck. Skipping the message.")
                    break
            except Exception as e:
                print(f"[TTS UNKNOWN ERROR]: Connection ERROR, TTS wont work (WOMP WOMP): {e}")
                break
            
            
    # ===========================
    #   AI Prompt Entry Point
    # ===========================      
    def ask_ai(self, user_prompt, context=None):
        """Called by main.py when the quesiton is submitted inteh prompt menu"""
        if context is None:
            context = {"mood": "curious", "pet_name": self.name}
        else:
            context["pet_name"] = self.name
            context["mood"] = context.get("mood", "aware")
            
        fallback = "My circuts are a bit fried come back later"
        self._start_ai_and_speach_thread(user_prompt, context, fallback)
        
    def _start_ai_and_speach_thread(self, prompt: str, context: dict, fallback_text: str):
        """Runs AI and call the TTS in sep thread to avoid freezing the main loop"""
        def worker():
            msg_to_speak = ""
            if self.brain:
                try:
                    ai_msg = self.brain.ask(prompt, context)
                    print(f"AI Response: {self.name}: {ai_msg}")
                    
                    self.current_text = ai_msg
                    #just show it for 7 secconds
                    self.display_timer = time.time() + 7
                    
                    msg_to_speak = ai_msg
                except Exception as e:
                    print(f"AI Worker failed: {e}. Falling back to static text.")
                    msg_to_speak = fallback_text
                    self.current_text = fallback_text
                    self.display_timer = time.time() + 5
            else:
                msg_to_speak = fallback_text
                self.current_text = fallback_text
                self.display_timer = time.time() + 5
            
            self._run_speech_sync(msg_to_speak)
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    # ===========================================
    #   MOOD & IDLE SPEECH
    # ===========================================
    def say_random_idle(self):
        if not self.data["idle_messages"]:
            return
            
        fallback_text = random.choice(self.data["idle_messages"])
        
        prompt = "Say somthing funny, positive, or relevant to system monitoring."
        context = {"mood" : "idle", "pet_name": self.name}
        
        self._start_ai_and_speach_thread(prompt, context, fallback_text)

    def say_for_mood(self, mood):
        text_from_json = self.data["mood_reactions"].get(mood)
        if not text_from_json:
            text_from_json = f"The system is {mood}. I have no special reactions."

        fallback_text = text_from_json
        
        prompt = f"React to the system baing in a '{mood}' state. Keep it brief and in character"
        context = {"mood" : mood, "pet_name" : self.name}
        
        self._start_ai_and_speach_thread(prompt, context, fallback_text)
        