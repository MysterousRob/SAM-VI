import os 
import pygame
import json
import time
import sys

# File imports
from control_menu import ControlMenu
from overlay_utils import make_window_overlay
from pet import Pet
from rust_core import CPU  
from prompt_menu import PromptMenu

def draw_speech_bubble(screen, text, pos):
    font = pygame.font.SysFont("Arial", 16)
    max_width = 250
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    
    line_height = font.get_linesize()
    bubble_height = len(lines) * line_height + 20
    bubble_width = max([font.size(l)[0] for l in lines]) + 20
    
    bubble_rect = pygame.Rect(pos[0] - (bubble_width // 2), pos[1] - bubble_height - 20, bubble_width, bubble_height)
    pygame.draw.rect(screen, (255, 255, 220), bubble_rect, border_radius=10)
    pygame.draw.rect(screen, (0, 0, 0), bubble_rect, 2, border_radius=10)
    
    for i, line in enumerate(lines):
        txt_surf = font.render(line.strip(), True, (0, 0, 0))
        screen.blit(txt_surf, (bubble_rect.x + 10, bubble_rect.y + 10 + (i * line_height)))

pygame.init()
pygame.mixer.init()

CONFIG_PATH = "config.json"
def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"current_theme": "dark", "ai_config": {"enabled": True, "backend": "local"}}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

config = load_config()

# Set up screen
screen = pygame.display.set_mode((1920, 1080), pygame.NOFRAME)
pygame.display.set_caption("Clippy Overlay")
make_window_overlay("Clippy Overlay")

clock = pygame.time.Clock()

# Initialize Pet
pet_path = config.get("last_pet", "assets/pets/Clippy/clippy2025_1.0.gif")
pet = Pet(pet_path, (1920, 1080))

# Initialize Rust Core
sim_cpu = CPU()

# Menu state
menu = None
menu_open = False
prompt_menu = None 
prompt_menu_open = False 

def open_control_menu():
    global menu, menu_open
    if not menu_open:
        x = pet.rect.x + pet.rect.width + 20
        y = pet.rect.y
        menu = ControlMenu(x, y, pet, config)
        menu_open = True
        
def close_control_menu():
    global menu, menu_open
    if menu_open:
        if menu: menu.close()
        menu = None
        menu_open = False
        
def open_prompt_menu():
    global prompt_menu, prompt_menu_open
    if not prompt_menu_open:
        x = pet.rect.x + (pet.rect.width // 2) - 200 
        y = pet.rect.y - 180 
        prompt_menu = PromptMenu(x, y)
        prompt_menu_open = True
        
def close_prompt_menu():
    global prompt_menu, prompt_menu_open
    if prompt_menu_open: 
        if prompt_menu: prompt_menu.close()
        prompt_menu = None 
        prompt_menu_open = False

running = True
while running:
    #refreshed the data
    #sim_cpu.refresh()
    #then grabs the statistics from backend
    stats = {
        "cpu_usage": sim_cpu.get_cpu_usage(),
        "gpu_usage": sim_cpu.get_gpu_usage(),
        "gpu_temp": sim_cpu.get_gpu_temp(),
        "cpu_temp": sim_cpu.get_temperature(), 
        "mem_usage": sim_cpu.get_memory_usage()
    }
    current_mood = pet.personality.update_mood_from_stats(stats)
    pet.update_from_mood(current_mood)
    pet.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if prompt_menu_open and prompt_menu:
            result = prompt_menu.handle_event(event)
            if result:
                if result.get("action") == "send":
                    # Pass context to the AI ask
                    pet.personality.ask_ai(result['prompt'], context={"stats": stats})
                    close_prompt_menu()
                elif result.get("action") == "close":
                    close_prompt_menu() 
            continue
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            if event.button == 3: # Right Click
                if menu_open: close_control_menu()
                else: open_control_menu()
                
            elif event.button == 1: # Left Click
                if menu_open and menu.rect.collidepoint(mx, my):
                    action = menu.handle_click((mx, my), pet_path)
                    if action == "Ask Pet": 
                        close_control_menu()
                        open_prompt_menu()
                elif menu_open:
                    close_control_menu()

    # Drawing
    screen.fill((0, 0, 0, 0)) 
    pet.draw(screen)
    
    if pet.personality.current_text and time.time() < pet.personality.display_timer:
        bubble_x = pet.rect.x + (pet.rect.width // 2)
        bubble_y = pet.rect.y
        draw_speech_bubble(screen, pet.personality.current_text, (bubble_x, bubble_y))
    elif pet.personality.current_text and time.time() >= pet.personality.display_timer:
        pet.personality.current_text = None
    
    if menu_open and menu:
        menu.draw(screen)
        
    if prompt_menu_open and prompt_menu:
        prompt_menu.draw(screen)
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()