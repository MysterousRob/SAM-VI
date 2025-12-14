import pygame
import json
import os
from rust_core import CPU
import math

CONFIG_PATH = "config.json"

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)


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
        labels = ["Themes", "CPU", "GPU", "Memory", "Power"]
        buttons = {}
        spacing_y = 50
        for i, label in enumerate(labels):
            buttons[label] = pygame.Rect(
                self.rect.x + 50, self.rect.y + 60 + i * spacing_y, 300, 40
            )
        return buttons  # fixed: moved return outside loop

    def draw(self, screen):
        # background
        pygame.draw.rect(screen, (30, 30, 40), self.rect, border_radius=15)
        pygame.draw.rect(screen, (150, 150, 180), self.rect, 2, border_radius=15)
        title = self.font.render("⚙️ Clippy Control Center", True, (255, 255, 255))
        screen.blit(title, (self.rect.x + 70, self.rect.y + 15))
        
        # draw buttons
        for label, rect in self.buttons.items():
            color = (80, 200, 255) if rect.collidepoint(pygame.mouse.get_pos()) else (180, 180, 180)
            pygame.draw.rect(screen, color, rect, border_radius=8)
            text = self.font.render(label, True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
        
        # button click detection
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            for label, rect in self.buttons.items():
                if rect.collidepoint(mx, my):
                    self.open_overlay(label)
                    
        if self.active_overlay:
            self.draw_overlay(screen)
        
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
                screen, color, 
                (x - radius, y - radius, radius * 2, radius * 2),
                start_angle, end_angle, thickness
            )
            
        # text
        text_surface = self.font.render(f"{self.overlay_type}: {percent:.1f}%", True, color)
        text_rect = text_surface.get_rect(center=(x, y + radius + 30))
        screen.blit(text_surface, text_rect)