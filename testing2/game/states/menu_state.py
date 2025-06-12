import pygame
from .base_state import BaseState
from ..constants import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK

class MenuState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('segoeuiemoji', 66)
        self.title = self.font.render("🎮 2D Roguelike RPG 🎮", True, WHITE)
        self.title_rect = self.title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        
        self.font_small = pygame.font.SysFont('segoeuiemoji', 28)
        self.start_text = self.font_small.render("🎲 Press SPACE to Start", True, WHITE)
        self.start_rect = self.start_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        
        self.quit_text = self.font_small.render("🚪 Press Q to Quit", True, WHITE)
        self.quit_rect = self.quit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game.change_state('game')
            elif event.key == pygame.K_q:
                self.game.running = False
                
    def update(self, dt):
        pass  # Menu state doesn't need any updates
        
    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(self.title, self.title_rect)
        screen.blit(self.start_text, self.start_rect)
        screen.blit(self.quit_text, self.quit_rect) 