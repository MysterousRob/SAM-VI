import os 
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any

class AIBrain(ABC):
    @abstractmethod
    def ask(self, prompt: str, context: Dict[str, Any] = {}) -> str:
        pass
    
class OpenAIBrain(AIBrain):
    """Placeholder for when you eventually get an API key"""
    def __init__(self, model: str = "gpt-3.5-turbo"):
        print("OpenAIBrain selected but not configured. Switching to Local logic.")
        
    def ask(self, prompt: str, context: Dict[str, Any] = {}) -> str:
        return "I need an API key for this! Try using the Local backend."

class LocalBrain(AIBrain):
    """Talks to Ollama running locally on your PC"""
    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.model = "gemma3:4b" 

    def ask(self, prompt: str, context: Dict[str, Any] = {}) -> str:
        system_rules = (
            "You are a sentient AI living inside a computer. "
            "You are quirky, a bit sarcastic, and very brief (under 15 words). "
            "React to the hardware stats if they are unusual."
        )
        stats = context.get('stats', {})
        cpu_load = stats.get('cpu_usage', 0)
        temp  = stats.get('temperature', 0)
        
        context_str = (
            f"Mood: {context.get('mood')},"
            f"CPU Load: {cpu_load:.1f}%,"
            f"Temp: {temp:.1f}°C"
        )
        
        full_prompt = f"{system_rules}\nSystem Status: {context_str}\nUser says: {prompt}"
        
        try:
            response = requests.post (
                self.url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("response", "internal logic error!!!").strip()
        except Exception as e:
            return "Ollama is offline. Start the Ollama app"