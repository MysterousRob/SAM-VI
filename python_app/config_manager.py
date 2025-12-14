import json
import os 

CONFIG_PATH = "config.json"

def save_last_pet(pet_path):
    """"Save ur last and hopefully final decision"""
    data = {"last_pet": pet_path}
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f)

def load_last_pet():
    """"load the last selected pet"""
    if not os.path.exists(CONFIG_PATH):
        return None
    try: 
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            return data.get("last_pet")
    except Exception:
        return None