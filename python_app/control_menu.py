import pygame
import json
import os
from rust_core import CPU
import math

try:
    from main import save_config
except ImportError:
    print("Unable to import save_config from main.py. It aint gonna work.")
    def save_config(cfg): pass


class ControlMenu:
    def __init__(self, x, y, pet, config):
        self.width, self.height = 400, 300
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.pet = pet
        self.config = config
        self.font = pygame.font.SysFont("Consolas", 20)
        self.buttons = self.create_buttons()
        self.cpu_core = CPU()
        
        self.active_overlay = False
        self.overlay_rect = None
        self.overlay_type = None
    
    def create_buttons(self):
        labels = ["Themes", "CPU", "GPU", "Memory", "Power", "Ask Me"]
        buttons = {}
        spacing_y = 50
        for i, label in enumerate(labels):
            buttons[label] = pygame.Rect(
                self.rect.x + 50, self.rect.y + 60 + i * spacing_y, 300, 40
            )
        return buttons 
    
    def close(self):
        """method to close the menu"""
        self.active_overlay = False
        self.overlay_type = None
    
    def handle_click(self, pos, pet_path):
        """menu click for the correct overly/function"""
        
        if self.buttons["Themes"].collidepoint(pos):
            current_theme = self.config.get("current_theme", "dark")
            new_theme = "light" if current_theme == "dark" else "dark"
            self.config["current_theme"] = new_theme
            
            save_config(self.config)
            
            print(f"Theme changed to: {new_theme}")
            return None
        
        if self.buttons["Ask Me"].collidepoint(pos):
            print("ASK ME clicked. opening the prompt menu.")
            self.close()
            return "Ask Me"
        
        for label in ["CPU", "GPU", "Memory", "Power"]:
            if self.buttons[label].collidepoint(pos):
                if self.active_overlay and self.overlay_type == label.lower():
                    self.active_overlay = False
                    self.overlay_type = None
                    print(f"Overlay {label} closed.")
                else:
                    self.active_overlay = True
                    self.overlay_type = label.lower()
                    self.overlay_rect = pygame.Rect(
                        self.rect.x + 400, self.rect.y, 200, 200
                    )
                    print(f"Overlay {label} opened.")
                return None
            

    def draw(self, screen):
        pygame.draw.rect(screen, (50, 50, 60), self.rect, border_radius=10)
        
        for label, rect in self.buttons.items():
            color = (100, 100, 100)
            text_color = (255, 255, 255)
            
            mx, my = pygame.mouse.get_pos()
            if rect.collidepoint(mx, my):
                color = (70, 70, 70)
            
            pygame.draw.rect(screen, color, rect, border_radius=5)
            text_surf = self.font.render(label, True, text_color)
            screen.blit(text_surf, (rect.x + 10, rect.y + 10))
            
        if self.active_overlay and self.overlay_type:
            if self.overlay_type == "cpu":
                value = self.cpu_core.get_temperature()
            else: 
                value = 50.0
            
            self.draw_gauge(screen, value, self.overlay_rect.center)
        
    def open_overlay(self, label):
        x, y = self.pet.rect.x + 100, self.pet.rect.y - 50
        self.overlay_rect = pygame.Rect(x, y, 300, 300)
        self.active_overlay = True
        self.overlay_type = label
        print(f"🧭 Opened overlay for: {label}")
        
    def draw_overlay(self, screen):
        if not self.overlay_type:
            return
        
        # background with glow
        s = pygame.Surface((self.overlay_rect.width, self.overlay_rect.height), pygame.SRCALPHA)
        s.fill((20, 25, 35, 220))
        pygame.draw.rect(s, (0, 255, 255, 60), s.get_rect(), border_radius=15)
        screen.blit(s, (self.overlay_rect.x, self.overlay_rect.y))
        
        # title 
        label = self.font.render(f"{self.overlay_type} Stats", True, (255, 255, 255))
        screen.blit(label, (self.overlay_rect.x + 80, self.overlay_rect.y + 20))
        
        # fetch metrics
        value = 0.0
        if self.overlay_type == "CPU":
            value = self.cpu_core.get_cpu_usage()
        elif self.overlay_type == "GPU":
            value = self.cpu_core.get_gpu_usage()
        elif self.overlay_type == "Memory":
            value = self.cpu_core.get_memory_usage()
        elif self.overlay_type == "Power":
            value = self.cpu_core.get_power_usage()
        else:
            value = 0.0
        
        # draw gauge
        self.draw_gauge(screen, value, self.overlay_rect.center)
        
        # close overlay when clicked outside
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if not self.overlay_rect.collidepoint(mx, my):
                print("❌ Overlay closed")
                self.active_overlay = False
                self.overlay_type = None
            
    def draw_gauge(self, screen, value, center):
        percent = max(0, min(100, value))
        radius = 80
        x, y = center
        
        # gauge color
        if percent < 50:
            color = (0, 255, 100)
        elif percent < 80:
            color = (255, 200, 0)
        else:
            color = (255, 60, 60)
        
        pygame.draw.circle(screen, (60, 60, 70), center, radius + 10, 10)
        
        # filled arc
        start_angle = -math.pi / 2
        end_angle = start_angle + (percent / 100.0) * 2 * math.pi
        for thickness in range(12, 20):
            pygame.draw.arc(
                screen, 
                color, 
                (x - radius, y - radius, radius * 2, radius * 2),
                start_angle, 
                end_angle, 
                thickness
            )
            
        # text
        value_text = self.font.render(f"{percent:.1f}%", True, color)
        screen.blit(value_text, (x - value_text.get_width() // 2, y - 10))