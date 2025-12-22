import pygame
import json
import os
from rust_core import CPU
import math

try:
    from main import save_config
except ImportError:
    def save_config(cfg): pass

class ControlMenu:
    def __init__(self, x, y, pet, config):
        self.width, self.height = 400, 350
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.pet = pet
        self.config = config
        self.font = pygame.font.SysFont("Consolas", 18)
        self.header_font = pygame.font.SysFont("Consolas", 22, bold=True)
        self.buttons = self.create_buttons()
        self.cpu_core = CPU()
        
        self.active_overlay = False
        self.overlay_rect = None
        self.overlay_type = None
    
    
    def close(self):
        """stops any crashes given  by main.py by the method its looking for"""
        self.active_overlay = False
        self.overlay_type = None
        
    def create_buttons(self):
        # We've renamed these to be "Dashboards" essentially
        labels = ["Themes", "CPU Stats", "GPU Stats", "Memory", "Ask Me"]
        buttons = {}
        spacing_y = 50
        for i, label in enumerate(labels):
            buttons[label] = pygame.Rect(
                self.rect.x + 50, self.rect.y + 40 + i * spacing_y, 300, 40
            )
        return buttons 
    
    def handle_click(self, pos, pet_path):
        if self.buttons["Themes"].collidepoint(pos):
            current_theme = self.config.get("current_theme", "dark")
            self.config["current_theme"] = "light" if current_theme == "dark" else "dark"
            save_config(self.config)
            return None
        
        if self.buttons["Ask Me"].collidepoint(pos):
            self.active_overlay = False
            return "Ask Me"
        
        # Dashboard Toggling Logic
        for label in ["CPU Stats", "GPU Stats", "Memory"]:
            if self.buttons[label].collidepoint(pos):
                l_lower = label.lower()
                if self.active_overlay and self.overlay_type == l_lower:
                    self.active_overlay = False
                    self.overlay_type = None
                else:
                    self.active_overlay = True
                    self.overlay_type = l_lower
                    
                    # DYNAMIC WIDTH: 3 gauges = 550px, 2 gauges = 400px, 1 gauge = 250px
                    if l_lower == "gpu stats":
                        width = 550
                    elif l_lower == "cpu stats":
                        width = 400
                    else:
                        width = 250
                    
                    self.overlay_rect = pygame.Rect(self.rect.x + 400, self.rect.y, width, 250)
                return None

    def draw(self, screen):
        # Draw the main command menu
        pygame.draw.rect(screen, (40, 40, 50, 240), self.rect, border_radius=15)
        pygame.draw.rect(screen, (0, 255, 255), self.rect, 2, border_radius=15)
        
        for label, rect in self.buttons.items():
            color = (80, 80, 100) if rect.collidepoint(pygame.mouse.get_pos()) else (60, 60, 70)
            pygame.draw.rect(screen, color, rect, border_radius=8)
            text_surf = self.font.render(label, True, (255, 255, 255))
            screen.blit(text_surf, (rect.x + 15, rect.y + 10))
            
        if self.active_overlay and self.overlay_rect:
            self.draw_overlay(screen)
        
    def draw_overlay(self, screen):
        # Semi-transparent dashboard background
        pygame.draw.rect(screen, (30, 30, 40, 240), self.overlay_rect, border_radius=15)
        pygame.draw.rect(screen, (0, 255, 255, 120), self.overlay_rect, 2, border_radius=15)
        
        w = self.overlay_rect.width
        
        if self.overlay_type == "cpu stats":
            usage = self.cpu_core.get_cpu_usage()
            temp = self.cpu_core.get_temperature()
            
            # Two-column layout
            c1 = (self.overlay_rect.x + w // 4, self.overlay_rect.centery + 20)
            c2 = (self.overlay_rect.x + (3 * w) // 4, self.overlay_rect.centery + 20)
            
            self.draw_gauge(screen, usage, usage, c1, "CPU LOAD", 60, "%")
            self.draw_gauge(screen, temp, temp, c2, "CPU TEMP", 60, "°C")

        elif self.overlay_type == "gpu stats":
            usage = self.cpu_core.get_gpu_usage()
            temp = self.cpu_core.get_gpu_temp()
            pwr = self.cpu_core.get_gpu_power()
            
            # Three-column layout
            c1 = (self.overlay_rect.x + w // 6, self.overlay_rect.centery + 20)
            c2 = (self.overlay_rect.x + w // 2, self.overlay_rect.centery + 20)
            c3 = (self.overlay_rect.x + (5 * w) // 6, self.overlay_rect.centery + 20)
            
            self.draw_gauge(screen, usage, usage, c1, "LOAD", 50, "%")
            self.draw_gauge(screen, temp, temp, c2, "TEMP", 50, "°C")
            self.draw_gauge(screen, (pwr/300.0)*100, pwr, c3, "POWER", 50, "W")
            
        elif self.overlay_type == "memory":
            val = self.cpu_core.get_memory_usage()
            self.draw_gauge(screen, val, val, self.overlay_rect.center, "RAM USED", 80, "%")

    def draw_gauge(self, screen, percent, display_val, center, label, radius, unit):
        percent = max(0, min(100, percent))
        x, y = center
        
        # Set color based on intensity
        if percent < 50: color = (0, 255, 150) # Green
        elif percent < 85: color = (255, 200, 0) # Yellow
        else: color = (255, 50, 50) # Red
        
        # Background Circle
        pygame.draw.circle(screen, (50, 50, 60), center, radius + 5, 8)
        
        # The Progress Arc
        rect = (x - radius, y - radius, radius * 2, radius * 2)
        start_angle = -math.pi / 2
        end_angle = start_angle + (percent / 100.0) * 2 * math.pi
        if percent > 0:
            pygame.draw.arc(screen, color, rect, start_angle, end_angle, 10)
            
        # Large value text in center
        val_text = self.header_font.render(f"{int(display_val)}{unit}", True, color)
        screen.blit(val_text, (x - val_text.get_width() // 2, y - 10))
        
        # Label text above gauge
        lbl_text = self.font.render(label, True, (200, 200, 200))
        screen.blit(lbl_text, (x - lbl_text.get_width() // 2, y - radius - 35))