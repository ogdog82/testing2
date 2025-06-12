import pygame
from ..constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, 
    BLACK, WHITE, RED, GREEN, BLUE, GRAY, YELLOW
)
from ..shop.shop_system import ShopSystem
from .base_state import BaseState

class ShopState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.shop_system = ShopSystem()
        self.selected_item = 0
        self.message = ""
        self.message_timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = max(0, self.selected_item - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_item = min(len(self.shop_system.inventory) - 1, self.selected_item + 1)
            elif event.key == pygame.K_b:
                success, message = self.shop_system.buy_item(self.game.player, self.selected_item)
                self.show_message(message)
            elif event.key == pygame.K_s:
                success, message = self.shop_system.sell_item(self.game.player, self.selected_item)
                self.show_message(message)
            elif event.key == pygame.K_r:
                self.shop_system.refresh_shop()
                self.show_message("Shop refreshed!")
            elif event.key == pygame.K_ESCAPE:
                # Return to game state
                self.game.change_state('game')
                return  # Ensure we exit immediately
                
    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            
    def render(self, screen):
        # Draw background
        screen.fill(BLACK)
        
        # Draw shop title
        title_font = pygame.font.SysFont('segoeuiemoji', 48)
        title_text = title_font.render("🏪 Shop", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 20))
        
        # Draw player gold
        gold_font = pygame.font.SysFont('segoeuiemoji', 36)
        gold_text = gold_font.render(f"💰 Gold: {self.game.player.inventory.gold}", True, YELLOW)
        screen.blit(gold_text, (20, 20))
        
        # Draw shop inventory
        y = 100
        for i, item in enumerate(self.shop_system.inventory):
            # Draw selection highlight
            if i == self.selected_item:
                pygame.draw.rect(screen, GRAY, (10, y - 5, WINDOW_WIDTH - 20, 100))
                
            # Draw item name and price
            item_font = pygame.font.SysFont('segoeuiemoji', 32)
            price = self.shop_system.item_system.get_item_value(item)
            item_text = item_font.render(f"{item['name']} - {price} gold", True, WHITE)
            screen.blit(item_text, (20, y))
            
            # Draw item stats
            stats_font = pygame.font.SysFont('segoeuiemoji', 24)
            stats_text = self.shop_system.item_system.get_item_description(item)
            stats_lines = stats_text.split('\n')
            for j, line in enumerate(stats_lines):
                stat_text = stats_font.render(line, True, WHITE)
                screen.blit(stat_text, (40, y + 30 + j * 20))
                
            y += 120
            
        # Draw controls
        controls_font = pygame.font.SysFont('segoeuiemoji', 24)
        controls = [
            "Controls:",
            "⬆️/⬇️: Select item",
            "B: Buy selected item",
            "S: Sell selected item",
            "R: Refresh shop",
            "ESC: Return to game"
        ]
        
        for i, control in enumerate(controls):
            control_text = controls_font.render(control, True, WHITE)
            screen.blit(control_text, (20, WINDOW_HEIGHT - 150 + i * 25))
            
        # Draw message
        if self.message_timer > 0:
            message_font = pygame.font.SysFont('segoeuiemoji', 32)
            message_text = message_font.render(self.message, True, WHITE)
            screen.blit(message_text, (WINDOW_WIDTH // 2 - message_text.get_width() // 2, WINDOW_HEIGHT - 50))
            
    def show_message(self, message):
        self.message = message
        self.message_timer = 1.0  # Show message for 1 second 