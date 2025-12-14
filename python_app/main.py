import os 
import pygame
#import openai 
import json
import time
from control_menu import ControlMenu
from overlay_utils import make_window_overlay
from pet import Pet
from rust_core import CPU
import psutil

#openai.api_key = os.environ.get("OPENAI_API_KEY")
#
#if not openai.api_key:
#    print("Error: OpenAI API key not set.  Please set the OPENAI_API_KEY environment variable.")
#    exit()
#
#try: 
#    response = openai.completions.create(
#        model="gpt-3.5-turbo",
#        prompt="",
#        max_tokens=150,
#        stop=None
#    )
#    for chunk in response:
#        if chunk.choices[0].delta['text']:
#            print(chunk.choices[0].delta['text'], end="", flush=True)
#        else:
#            break
#        
#except openai.OpenAIError as e:
#    print(f"OpenAI API error: {e}")


pygame.init()
pygame.mixer.init()

# --- CONFIG ---
CONFIG_PATH = "config.json"
def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"currnet_theme": "Dark"}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)
        
config = load_config()


screen = pygame.display.set_mode((1000, 700), pygame.NOFRAME)
pygame.display.set_caption("Clippy Overlay")
make_window_overlay("Clippy Overlay")

clock = pygame.time.Clock()

pet_path = config.get("last_pet", "assets/pets/Clippy/clippy2025_1.0.gif")
pet = Pet(pet_path, (1000, 700))
sim_cpu = CPU()

menu = None
menu_open = False

def open_control_menu():
    global menu, menu_open
    if not menu_open:
        print("Controll menu open")
        x, y = pet.rect.x + 80, pet.rect.y + 50
        menu = ControlMenu(x, y, pet, config)
        menu_open = True
        
def close_control_menu():
    global menu, menu_open
    if menu_open:
        print("Control menu Closed")
        menu = None
        menu_open = False
            
            
def get_system_metrics():
    metrics = {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "mem_percent": psutil.virtual_memory().percent,
    }
    return metrics
            
            

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                print("Right click detected")
                open_control_menu()
            elif event.button == 1 and menu_open:
                print("Left click detected")
                mx, my = pygame.mouse.get_pos()
                
                if not menu.rect.collidepoint(mx, my):
                    close_control_menu()
                    continue
    
    sim_cpu.execute("ADD", 0, 1)
    sys_data = get_system_metrics()
    sim_temp = sim_cpu.get_temperature()
    sim_power = sim_cpu.get_power_usage()
    mixed_temp = (sim_temp + sys_data["cpu_percent"]) / 2
    mixed_power = (sim_power + sys_data["mem_percent"] / 10) / 2
    
    
    pet.update(mixed_temp, mixed_power)
    screen.fill((25, 25, 30))
    pet.draw(screen)
    
    if menu_open and menu:
        menu.draw(screen)
    
    pygame.display.flip()
    clock.tick(30)
    time.sleep(0.05)

pygame.quit()