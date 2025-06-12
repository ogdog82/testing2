import pygame
from .base_state import BaseState
from ..constants import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK

class GameOverState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('segoeuiemoji', 66)
        self.game_over_text = self.font.render("💀 Game Over 💀", True, WHITE)
        self.game_over_rect = self.game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        
        self.font_small = pygame.font.SysFont('segoeuiemoji', 28)
        self.restart_text = self.font_small.render("🔄 Press SPACE to Restart", True, WHITE)
        self.restart_rect = self.restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        
        self.menu_text = self.font_small.render("🏠 Press M for Main Menu", True, WHITE)
        self.menu_rect = self.menu_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game.change_state('game')
            elif event.key == pygame.K_m:
                self.game.change_state('menu')
                
    def update(self, dt):
        pass  # Game over state doesn't need any updates
        
    def render(self, screen):
        screen.fill(BLACK)
        screen.blit(self.game_over_text, self.game_over_rect)
        screen.blit(self.restart_text, self.restart_rect)
        screen.blit(self.menu_text, self.menu_rect) 