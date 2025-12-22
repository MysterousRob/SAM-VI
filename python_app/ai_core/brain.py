import requests
import json
from typing import Dict, Any

class LocalBrain:
    def __init__(self):
        self.model = "gemma3:4b" 
        self.url = "http://localhost:11434/api/generate"
        
        self.system_rules = (
            "You are Clippy, a sarcastic but helpful desktop pet. "
            "You monitor the user's computer hardware. Keep your answers short (1-2 sentences). "
            "If the CPU is hot, be worried. If the RAM is full, complain about it."
        )

    def ask(self, user_query: str, context: Dict[str, Any] = {}) -> str:
        """Sends a prompt to Ollama with hardware stats as context."""
        
        stats = context.get("stats", {})
        stats_str = (
            f"Current Stats: CPU: {stats.get('cpu_usage')}% at {stats.get('cpu_temp')}°C, "
            f"GPU: {stats.get('gpu_usage')}% at {stats.get('gpu_temp')}°C, "
            f"RAM: {stats.get('mem_usage')}%."
        )

        full_prompt = f"{self.system_rules}\n\n{stats_str}\n\nUser says: {user_query}\nClippy:"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False  
        }

        try:
            response = requests.post(self.url, json=payload, timeout=15)
            
            if response.status_code == 200:
                return response.json().get("response", "I have no words... literally.")
            else:
                return f"Ollama Error {response.status_code}: Is the model pulled?"
                
        except requests.exceptions.ConnectionError:
            return "I can't reach my brain! (Ollama is offline)"
        except Exception as e:
            return f"Brain Glitch: {str(e)}"