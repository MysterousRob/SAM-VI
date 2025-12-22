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
        self.width, self.height = 400, 350 # Increased height for more buttons
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.pet = pet
        self.config = config
        self.font = pygame.font.SysFont("Consolas", 20)
        # Added a bold font for the center values
        self.header_font = pygame.font.SysFont("Consolas", 22, bold=True)
        self.buttons = self.create_buttons()
        self.cpu_core = CPU()
        
        self.active_overlay = False
        self.overlay_rect = None
        self.overlay_type = None
    
    def create_buttons(self):
        # Changed "GPU" to "GPU Stats" to reflect the new dashboard
        labels = ["Themes", "CPU", "GPU Stats", "Memory", "Ask Me"]
        buttons = {}
        spacing_y = 50
        for i, label in enumerate(labels):
            buttons[label] = pygame.Rect(
                self.rect.x + 50, self.rect.y + 40 + i * spacing_y, 300, 40
            )
        return buttons 
    
    def close(self):
        self.active_overlay = False
        self.overlay_type = None
    
    def handle_click(self, pos, pet_path):
        if self.buttons["Themes"].collidepoint(pos):
            current_theme = self.config.get("current_theme", "dark")
            new_theme = "light" if current_theme == "dark" else "dark"
            self.config["current_theme"] = new_theme
            save_config(self.config)
            return None
        
        if self.buttons["Ask Me"].collidepoint(pos):
            self.close()
            return "Ask Me"
        
        for label in ["CPU", "GPU Stats", "Memory"]:
            if self.buttons[label].collidepoint(pos):
                l_lower = label.lower()
                if self.active_overlay and self.overlay_type == l_lower:
                    self.active_overlay = False
                    self.overlay_type = None
                else:
                    self.active_overlay = True
                    self.overlay_type = l_lower
                    # TOGGLE WINDOW WIDTH: Wider (550) for triple gauges, narrow (250) for others
                    width = 550 if l_lower == "gpu stats" else 250
                    self.overlay_rect = pygame.Rect(
                        self.rect.x + 400, self.rect.y, width, 250
                    )
                return None
            

    def draw(self, screen):
        # Draw Main Menu
        pygame.draw.rect(screen, (40, 40, 50, 240), self.rect, border_radius=15)
        pygame.draw.rect(screen, (0, 255, 255), self.rect, 2, border_radius=15)
        
        for label, rect in self.buttons.items():
            color = (60, 60, 70)
            mx, my = pygame.mouse.get_pos()
            if rect.collidepoint(mx, my):
                color = (80, 80, 100)
            
            pygame.draw.rect(screen, color, rect, border_radius=8)
            text_surf = self.font.render(label, True, (255, 255, 255))
            screen.blit(text_surf, (rect.x + 15, rect.y + 10))
            
        if self.active_overlay and self.overlay_rect:
            self.draw_overlay(screen)
        
    def draw_overlay(self, screen):
        # Background
        pygame.draw.rect(screen, (30, 30, 40, 240), self.overlay_rect, border_radius=15)
        pygame.draw.rect(screen, (0, 255, 255, 120), self.overlay_rect, 2, border_radius=15)
        
        if self.overlay_type == "gpu stats":
            # Fetch all three metrics from Rust
            usage = self.cpu_core.get_gpu_usage()
            temp = self.cpu_core.get_gpu_temp()
            power = self.cpu_core.get_gpu_power()
            
            w = self.overlay_rect.width
            # Position centers in 3 columns
            c1 = (self.overlay_rect.x + w // 6, self.overlay_rect.centery + 20)
            c2 = (self.overlay_rect.x + w // 2, self.overlay_rect.centery + 20)
            c3 = (self.overlay_rect.x + (5 * w) // 6, self.overlay_rect.centery + 20)
            
            # Draw the 3 gauges with specific units and labels
            self.draw_gauge(screen, usage, usage, c1, "LOAD", 50, "%")
            self.draw_gauge(screen, temp, temp, c2, "TEMP", 50, "°C")
            # Power scaled against 300W for the ring fill
            self.draw_gauge(screen, (power/300.0)*100, power, c3, "POWER", 50, "W")
            
        elif self.overlay_type == "cpu":
            val = self.cpu_core.get_cpu_usage()
            self.draw_gauge(screen, val, val, self.overlay_rect.center, "CPU LOAD", 80, "%")
            
        elif self.overlay_type == "memory":
            val = self.cpu_core.get_memory_usage()
            self.draw_gauge(screen, val, val, self.overlay_rect.center, "RAM USED", 80, "%")

    def draw_gauge(self, screen, percent, display_val, center, label, radius, unit):
        percent = max(0, min(100, percent))
        x, y = center
        
        # Dynamic color scale
        if percent < 50: color = (0, 255, 150)
        elif percent < 85: color = (255, 200, 0)
        else: color = (255, 50, 50)
        
        # Outer track
        pygame.draw.circle(screen, (50, 50, 60), center, radius + 5, 8)
        
        # Progress Arc
        rect = (x - radius, y - radius, radius * 2, radius * 2)
        start_angle = -math.pi / 2
        end_angle = start_angle + (percent / 100.0) * 2 * math.pi
        
        if percent > 0:
            pygame.draw.arc(screen, color, rect, start_angle, end_angle, 10)
            
        # Center numerical value
        val_text = self.header_font.render(f"{int(display_val)}{unit}", True, color)
        screen.blit(val_text, (x - val_text.get_width() // 2, y - 10))
        
        # Descriptive Label above the gauge
        lbl_text = self.font.render(label, True, (200, 200, 200))
        screen.blit(lbl_text, (x - lbl_text.get_width() // 2, y - radius - 35))