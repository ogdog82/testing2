import pygame
import math
from .base_state import BaseState
from ..constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    BLACK, WHITE, RED, GREEN, BLUE, GRAY, YELLOW
)

class InventoryState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.tabs = ['Inventory', 'Equipment', 'Skills', 'Stats']
        self.selected_tab = 0
        self.selected_item = None
        
        # Fonts
        self.font_large = pygame.font.SysFont('segoeuiemoji', 40)
        self.font_medium = pygame.font.SysFont('segoeuiemoji', 24)
        self.font_small = pygame.font.SysFont('segoeuiemoji', 16)
        
        # Icons
        self.tab_icons = {
            'Inventory': '🎒',
            'Equipment': '⚔️',
            'Skills': '✨',
            'Stats': '📊'
        }
        
        self.item_icons = {
            'weapon': '🗡️',
            'armor': '🛡️',
            'accessory': '💍',
            'consumable': '🧪'
        }
        
        self.equipment_icons = {
            'weapon': '⚔️',
            'armor': '🛡️',
            'accessory': '💍'
        }
        
        self.skill_icons = {
            'Fireball': '🔥',
            'Ice Nova': '❄️',
            'Lightning Strike': '⚡',
            'Heal': '💚'
        }
        
        # Colors
        self.rarity_colors = {
            'common': (200, 200, 200),    # White
            'uncommon': (0, 255, 0),      # Green
            'rare': (0, 0, 255),          # Blue
            'legendary': (255, 165, 0)    # Orange
        }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state('game')
            elif event.key == pygame.K_TAB:
                # Switch tabs
                self.selected_tab = (self.selected_tab + 1) % len(self.tabs)
                self.selected_item = None
            elif event.key == pygame.K_UP:
                # Move selection up
                if self.selected_tab == 0:  # Inventory
                    if self.selected_item is None:
                        self.selected_item = 0
                    else:
                        self.selected_item = max(0, self.selected_item - items_per_row)
                elif self.selected_tab == 1:  # Equipment
                    if self.selected_item is None:
                        self.selected_item = 0
                    else:
                        self.selected_item = max(0, self.selected_item - 1)
            elif event.key == pygame.K_DOWN:
                # Move selection down
                if self.selected_tab == 0:  # Inventory
                    if self.selected_item is None:
                        self.selected_item = 0
                    else:
                        self.selected_item = min(len(self.game.player.inventory.items) - 1,
                                              self.selected_item + items_per_row)
                elif self.selected_tab == 1:  # Equipment
                    if self.selected_item is None:
                        self.selected_item = 0
                    else:
                        self.selected_item = min(len(self.game.player.equipment) - 1,
                                              self.selected_item + 1)
            elif event.key == pygame.K_LEFT:
                # Move selection left
                if self.selected_tab == 0:  # Inventory
                    if self.selected_item is None:
                        self.selected_item = 0
                    else:
                        self.selected_item = max(0, self.selected_item - 1)
            elif event.key == pygame.K_RIGHT:
                # Move selection right
                if self.selected_tab == 0:  # Inventory
                    if self.selected_item is None:
                        self.selected_item = 0
                    else:
                        self.selected_item = min(len(self.game.player.inventory.items) - 1,
                                              self.selected_item + 1)
            elif event.key == pygame.K_RETURN:
                # Use/equip selected item
                if self.selected_tab == 0 and self.selected_item is not None:
                    item = self.game.player.inventory.items[self.selected_item]
                    if item.get('type') == 'consumable':
                        if self.game.player.use_consumable(item):
                            self.game.player.inventory.remove_item(item)
                    else:
                        self.game.player.equip_item(item)
                elif self.selected_tab == 1 and self.selected_item is not None:
                    slot = list(self.game.player.equipment.keys())[self.selected_item]
                    self.game.player.unequip_item(slot)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicked on a tab
                tab_width = 150
                tab_height = 40
                tab_spacing = 10
                tab_y = self.panel_y - tab_height - 10
                
                for i, tab in enumerate(self.tabs):
                    tab_x = self.panel_x + (tab_width + tab_spacing) * i
                    tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
                    if tab_rect.collidepoint(event.pos):
                        self.selected_tab = i
                        self.selected_item = None
                        return
                        
                # Check if clicked on an item
                if self.selected_tab == 0:  # Inventory
                    item_size = 60
                    items_per_row = 6
                    padding = 10
                    
                    for i, item in enumerate(self.game.player.inventory.items):
                        item_x = self.panel_x + 20 + padding + (i % items_per_row) * (item_size + padding)
                        item_y = self.panel_y + 20 + padding + (i // items_per_row) * (item_size + padding)
                        item_rect = pygame.Rect(item_x, item_y, item_size, item_size)
                        
                        if item_rect.collidepoint(event.pos):
                            self.selected_item = i
                            # Use/equip item on click
                            if item.get('type') == 'consumable':
                                if self.game.player.use_consumable(item):
                                    self.game.player.inventory.remove_item(item)
                            else:
                                self.game.player.equip_item(item)
                            return
                            
                elif self.selected_tab == 1:  # Equipment
                    slot_size = 50
                    padding = 10
                    
                    for i, (slot, item) in enumerate(self.game.player.equipment.items()):
                        item_x = self.panel_x + 20 + padding + (i % 6) * (slot_size + padding)
                        item_y = self.panel_y + 20 + padding + (i // 6) * (slot_size + padding)
                        item_rect = pygame.Rect(item_x, item_y, slot_size, slot_size)
                        
                        if item_rect.collidepoint(event.pos):
                            self.selected_item = i
                            if item:  # If there's an item equipped
                                self.game.player.unequip_item(slot)
                            return

    def update(self, dt):
        pass  # No continuous updates needed
        
    def render(self, screen):
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))
        
        # Draw main panel
        panel_width = 800
        panel_height = 600
        panel_x = (WINDOW_WIDTH - panel_width) // 2
        panel_y = (WINDOW_HEIGHT - panel_height) // 2
        
        # Draw panel background with gradient
        for i in range(5):  # Create gradient effect
            alpha = 200 - (i * 20)
            pygame.draw.rect(overlay, (40, 40, 40, alpha),
                (panel_x + i, panel_y + i, panel_width - (i * 2), panel_height - (i * 2)))
        
        # Draw panel border
        pygame.draw.rect(overlay, (100, 100, 100, 255),
            (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw tabs
        tab_width = 150
        tab_height = 40
        tab_spacing = 10
        tab_y = panel_y - tab_height - 10
        
        for i, tab in enumerate(self.tabs):
            tab_x = panel_x + (tab_width + tab_spacing) * i
            tab_color = (60, 60, 60, 255) if i != self.selected_tab else (80, 80, 80, 255)
            tab_border = (100, 100, 100, 255) if i != self.selected_tab else (150, 150, 150, 255)
            
            # Draw tab background
            pygame.draw.rect(overlay, tab_color,
                (tab_x, tab_y, tab_width, tab_height))
            pygame.draw.rect(overlay, tab_border,
                (tab_x, tab_y, tab_width, tab_height), 2)
            
            # Draw tab text with icon
            tab_text = f"{self.tab_icons[tab]} {tab}"
            text_surface = self.font_small.render(tab_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(tab_x + tab_width//2, tab_y + tab_height//2))
            overlay.blit(text_surface, text_rect)
        
        # Draw content based on selected tab
        content_x = panel_x + 20
        content_y = panel_y + 20
        content_width = panel_width - 40
        content_height = panel_height - 40
        
        if self.selected_tab == 0:  # Inventory
            self._draw_inventory(overlay, content_x, content_y, content_width, content_height)
        elif self.selected_tab == 1:  # Equipment
            self._draw_equipment(overlay, content_x, content_y, content_width, content_height)
        elif self.selected_tab == 2:  # Skills
            self._draw_skills(overlay, content_x, content_y, content_width, content_height)
        elif self.selected_tab == 3:  # Stats
            self._draw_stats(overlay, content_x, content_y, content_width, content_height)
        
        # Draw controls help
        controls_y = panel_y + panel_height + 10
        controls = [
            "TAB: Switch Tabs",
            "Click: Select/Use Item",
            "ESC: Close"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.font_small.render(control, True, (200, 200, 200))
            overlay.blit(control_text, (panel_x + (i * 180), controls_y))
        
        # Draw the overlay
        screen.blit(overlay, (0, 0))

    def _draw_inventory(self, surface, x, y, width, height):
        # Draw inventory grid
        item_size = 60
        items_per_row = 6
        padding = 10
        
        # Draw grid background
        grid_width = items_per_row * (item_size + padding) + padding
        grid_height = ((len(self.game.player.inventory.items) - 1) // items_per_row + 1) * (item_size + padding) + padding
        pygame.draw.rect(surface, (30, 30, 30, 255),
            (x, y, grid_width, grid_height))
        
        # Draw items
        for i, item in enumerate(self.game.player.inventory.items):
            item_x = x + padding + (i % items_per_row) * (item_size + padding)
            item_y = y + padding + (i // items_per_row) * (item_size + padding)
            
            # Draw item background
            bg_color = (50, 50, 50, 255)
            if i == self.selected_item:
                bg_color = (70, 70, 70, 255)
            pygame.draw.rect(surface, bg_color,
                (item_x, item_y, item_size, item_size))
            
            # Draw item icon
            icon = self.item_icons.get(item['type'], '❓')
            icon_surface = self.font_large.render(icon, True, (255, 255, 255))
            icon_rect = icon_surface.get_rect(center=(item_x + item_size//2, item_y + item_size//2))
            surface.blit(icon_surface, icon_rect)
            
            # Draw item name and effects
            if i == self.selected_item:
                # Draw item details panel
                details_x = x + grid_width + 20
                details_y = y
                details_width = width - grid_width - 40
                
                # Draw item name with rarity color
                name_color = self.rarity_colors.get(item.get('rarity', 'common'), (255, 255, 255))
                name_surface = self.font_medium.render(item.get('name', 'Unknown'), True, name_color)
                surface.blit(name_surface, (details_x, details_y))
                
                # Draw item description
                description = item.get('description', f"A {item['type']} item.")
                desc_surface = self.font_small.render(description, True, (200, 200, 200))
                surface.blit(desc_surface, (details_x, details_y + 30))
                
                # Draw item stats
                if 'stats' in item:
                    stats_y = details_y + 60
                    for stat, value in item['stats'].items():
                        stat_text = f"{stat}: {value}"
                        stat_surface = self.font_small.render(stat_text, True, (200, 200, 200))
                        surface.blit(stat_surface, (details_x, stats_y))
                        stats_y += 25

    def _draw_equipment(self, surface, x, y, width, height):
        slot_size = 50
        padding = 10
        start_y = 60
        
        for i, (slot, item) in enumerate(self.game.player.equipment.items()):
            item_x = x + padding + (i % 6) * (slot_size + padding)
            item_y = y + padding + (i // 6) * (slot_size + padding)
            
            # Draw slot background
            slot_rect = pygame.Rect(item_x, item_y, slot_size, slot_size)
            color = (100, 100, 100, 192) if i == self.selected_item else (50, 50, 50, 192)
            pygame.draw.rect(surface, color, slot_rect)
            pygame.draw.rect(surface, (255, 255, 255, 192), slot_rect, 2)
            
            # Draw slot name
            slot_text = self.font_small.render(slot.capitalize(), True, (255, 255, 255))
            surface.blit(slot_text, (item_x, item_y - 20))
            
            if item:
                # Draw item icon
                icon = self.item_icons.get(item['type'], '❓')
                icon_surface = self.font_large.render(icon, True, (255, 255, 255))
                icon_rect = icon_surface.get_rect(center=slot_rect.center)
                surface.blit(icon_surface, icon_rect)
                
                # Draw item name
                name_surface = self.font_small.render(item['name'], True, (255, 255, 255))
                surface.blit(name_surface, (item_x + slot_size + 10, item_y))
                
                # Draw item stats if selected
                if i == self.selected_item:
                    stats_x = item_x + slot_size + 10
                    stats_y = item_y + 20
                    
                    # Draw item description
                    desc_surface = self.font_small.render(item['description'], True, (200, 200, 200))
                    surface.blit(desc_surface, (stats_x, stats_y))
                    
                    # Draw item stats
                    if 'stats' in item:
                        stats_y += 30
                        for stat, value in item['stats'].items():
                            stat_text = f"{stat}: {value}"
                            stat_surface = self.font_small.render(stat_text, True, (200, 200, 200))
                            surface.blit(stat_surface, (stats_x, stats_y))
                            stats_y += 20

    def _draw_skills(self, surface, x, y, width, height):
        # Draw skills grid
        skill_size = 100
        skills_per_row = 4
        padding = 20
        
        for i, (skill_name, skill) in enumerate(self.game.player.skills.items()):
            skill_x = x + (i % skills_per_row) * (skill_size + padding)
            skill_y = y + (i // skills_per_row) * (skill_size + padding)
            
            # Draw skill background
            bg_color = (40, 40, 40, 255)
            if skill['current_cooldown'] > 0:
                bg_color = (30, 30, 30, 255)
            pygame.draw.rect(surface, bg_color,
                (skill_x, skill_y, skill_size, skill_size))
            pygame.draw.rect(surface, (100, 100, 100, 255),
                (skill_x, skill_y, skill_size, skill_size), 2)
                
            # Draw skill icon
            icon = self.skill_icons.get(skill['name'], '❓')
            icon_surface = self.font_large.render(icon, True, (255, 255, 255))
            icon_rect = icon_surface.get_rect(center=(skill_x + skill_size//2, skill_y + skill_size//2))
            surface.blit(icon_surface, icon_rect)
            
            # Draw skill name with smaller font
            name_surface = self.font_small.render(skill['name'], True, (200, 200, 200))
            name_rect = name_surface.get_rect(center=(skill_x + skill_size//2, skill_y + skill_size - 15))
            surface.blit(name_surface, name_rect)
            
            # Draw cooldown overlay
            if skill['current_cooldown'] > 0:
                cooldown_height = (skill['current_cooldown'] / skill['cooldown']) * skill_size
                cooldown_rect = pygame.Rect(skill_x, skill_y + skill_size - cooldown_height,
                    skill_size, cooldown_height)
                pygame.draw.rect(surface, (0, 0, 0, 128), cooldown_rect)
                
                # Draw cooldown text
                cooldown_text = f"{int(skill['current_cooldown'])}s"
                cooldown_surface = self.font_small.render(cooldown_text, True, (255, 255, 255))
                cooldown_rect = cooldown_surface.get_rect(center=(skill_x + skill_size//2, skill_y + skill_size//2))
                surface.blit(cooldown_surface, cooldown_rect)
                
    def _draw_stats(self, surface, x, y, width, height):
        # Draw stats panel
        panel_width = 300
        panel_height = 200
        panel_x = x + 100
        panel_y = y + 20
        
        # Draw panel background
        pygame.draw.rect(surface, (40, 40, 40, 255),
            (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, (100, 100, 100, 255),
            (panel_x, panel_y, panel_width, panel_height), 2)
            
        # Calculate base stats
        base_stats = {
            'strength': 10 + (self.game.player.level - 1) * 2,
            'dexterity': 10 + (self.game.player.level - 1) * 2,
            'intelligence': 10 + (self.game.player.level - 1) * 2,
            'vitality': 10 + (self.game.player.level - 1) * 2
        }
        
        # Draw stats
        stats_y = panel_y + 20
        for stat, value in self.game.player.stats.items():
            # Draw stat name
            stat_text = f"{stat.capitalize()}:"
            stat_surface = self.font_small.render(stat_text, True, (200, 200, 200))
            surface.blit(stat_surface, (panel_x + 20, stats_y))
            
            # Draw stat value with bonus
            bonus = value - base_stats[stat]
            if bonus > 0:
                value_text = f"{value} (+{bonus})"
                value_color = (0, 255, 0)  # Green for positive bonus
            else:
                value_text = str(value)
                value_color = (255, 255, 255)
                
            value_surface = self.font_small.render(value_text, True, value_color)
            surface.blit(value_surface, (panel_x + 150, stats_y))
            
            stats_y += 30 