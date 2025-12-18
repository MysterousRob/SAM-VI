import pygame
import os 


pygame.font.init()
try:
    DEFAULT_FONT = pygame.font.SysFont("Consolas", 20)
except:
    DEFAULT_FONT = pygame.font.Font(None, 24)
    

class PromptMenu:
    def __init__(self, x, y):
        #geometry paramaters
        self.width, self.height = 400, 150
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        self.input_rect = pygame.Rect(x + 20, y + 60, 360, 40)
        
        self.font = DEFAULT_FONT
        
        #State variables
        self.prompt_text = ""
        self.max_length = 35
        self.is_active = True
        
        
        #entry points
        self.color_interactive = (150, 150, 150)
        self.color_active =  (255, 255, 255)
        self.color = self.color_active
        self.bg_color = (35, 35, 45, 220)
        self.text_color = (255, 255, 255)
        
        print("Promp Menu Opened.")
        
    def handle_event(self, event):
        """keyboard shortcuts"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                sent_prompt = self.prompt_text.strip()
                if sent_prompt:
                    print(f"Prompt Sent: {sent_prompt}")
                    ##commenting out bc main.py destroys the menu obj immediately
                    #self.prompt_text = ""
                    return {"action": "send", "prompt": sent_prompt}
                
            elif event.key == pygame.K_BACKSPACE:
                self.prompt_text = self.prompt_text[:-1]
            
            elif event.key == pygame.K_ESCAPE:
                return {"action": "close"}
            
            else:
                if len(self.prompt_text) < self.max_length:
                    char = event.unicode
                    if char.isprintable() and char != "":
                        self.prompt_text += char
        
        return None
    
    def draw(self, screen):
        """draws the prompt window"""
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=10)
        
        pygame.draw.rect(screen, self.color_active, self.input_rect, 2, border_radius=5)
        
        title_surf = self.font.render("Ask Clippy(ESC to close):", True, self.text_color)
        screen.blit(title_surf, (self.rect.x + 20, self.rect.y + 20))
        
        display_text = self.prompt_text
        if (pygame.time.get_tics() // 500) % 2 == 0:
            display_text += "|"
        
        txt_surface = self.font.render(display_text, True, self.text_color)
        
        if txt_surface.get() > self.input_rect.width - 10:
            display_text = display_text[-(self.max_length):]
            txt_surface = self.font.render(display_text, True, self.text_color)
        
        screen.blit(txt_surface, (self.input_rect.x + 5, self.input_rect.y + 8))

    def close(self):
        """close the menu"""
        self.is_active = False