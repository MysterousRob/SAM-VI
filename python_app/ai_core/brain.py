import os 
from abc import ABC, abstractmethod
from typing import Dict, Any

try: 
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("OpenAI library not found. Install it with: pip install openai")

class AIBrain(ABC):
    """Abstract class for model integration"""
    @abstractmethod
    def ask(self, prompt: str, context: Dict[str, Any] = {}) -> str:
        """Takes a prompt and context, and return a short string response."""
        pass
    
class OpenAIBrain(AIBrain):
    """Concrete implimentation using the OpenAI API"""
    def __init__(self, model: str = "gpt-3.5-turbo"):
        if OpenAI is None:
            raise RuntimeError("OpenAI library is required for OpenAIBrain")
        
        self.client = OpenAI(api_key=os.envireomn.get("OPENAI_API_KEY"))
        if not self.client.api_key:
            raise ValueError("OPENAI_API_KEY enviroment variable not set.")
        self.model = model
        print(f"AI Brain initialized: OpenAI ({self.model})")
        
        def ask(self, prompt: str, context: Dict[str, Any] = {}) -> str: 
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            
            system_message = (
                "You are a helpful, quirky, and friendly desktop assistant. "
                "Keep your responces very shory, like a real desktop pet would talk. "
                "Limit your answer to one short sentence or phrase (max 15 words). "
            )
            
            messages = [
                {"role": "system", "context": system_message},
                {"role": "user", "content": f"{context_str}\n\nTask: {prompt}"}
            ]
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=30,
                    temperature=0.7,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"SpenAI API call failed: {e}")
                return "My circuts are buzzing! I cant talk right now."

class LocalBrain(AIBrain):
    """Placeholder for LLM integration"""
    def __init__(self):
        def ask(self, prompt:str, context: Dict[str, Any] = {}) -> str:
            mood = context.get("mood")
            if mood == "idle":
                return "im thinking about... bytes n Stuff"
            elif mood == "overheateed":
                return "Woah, Im burning up! too Much math"
            else:
                return f"my local memory is busy"