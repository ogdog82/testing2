import pygame
import random
import math
from .base_state import BaseState
from ..entities.player import Player
from ..entities.enemy import Enemy
from ..dungeon.dungeon_generator import DungeonGenerator
from ..constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    BLACK, WHITE, RED, GREEN, BLUE, GRAY, YELLOW,
    UI_PADDING, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT,
    MANA_BAR_WIDTH, MANA_BAR_HEIGHT,
    SKILL_ICON_SIZE, DUNGEON_WIDTH, DUNGEON_HEIGHT,
    PLAYER_KNOCKBACK_FORCE, PLAYER_KNOCKBACK_DURATION
)

class GameState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.screen_width = WINDOW_WIDTH
        self.screen_height = WINDOW_HEIGHT
        self.tile_size = 32
        self.dungeon_width = DUNGEON_WIDTH
        self.dungeon_height = DUNGEON_HEIGHT
        self.current_level = 1
        self.camera_x = 0
        self.camera_y = 0
        
        # Attack visualization
        self.attack_arcs = []  # List of active attack arcs
        self.attack_animation_duration = 0.05  # Reduced from 0.1 to 0.05 seconds
        self.attack_animation_progress = 0  # Current progress of the animation
        
        # Attack effect colors
        self.attack_colors = {
            'primary': (255, 255, 255, 128),  # White with reduced opacity
            'secondary': (200, 200, 200, 96),  # Light gray with reduced opacity
            'trail': (100, 100, 100, 64),  # Dark gray with reduced opacity
            'glow': (50, 50, 50, 32)  # Very dark gray with reduced opacity
        }
        
        # Use the game's dungeon and player
        self.dungeon_generator = game.dungeon_generator
        self.dungeon_grid = game.dungeon_grid
        self.player = game.player
        
        # Initialize enemies
        self.enemies = []
        self._spawn_enemies(5)  # Start with 5 enemies
        
        # UI elements
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)
        
        # Generate random dungeon colors
        self._generate_dungeon_colors()
        
        # Drops
        self.drops = []
        
        # Shop cooldown
        self.shop_cooldown = 0
        self.shop_cooldown_duration = 5  # 5 seconds cooldown
        
    def _generate_dungeon_colors(self):
        # Dungeon-appropriate colors with clear distinction between floors and walls
        floor_colors = [
            (139, 69, 19),    # Brown
            (101, 67, 33),    # Dark Brown
            (85, 107, 47),    # Dark Olive Green
            (139, 137, 137),  # Light Gray
            (169, 169, 169),  # Dark Gray
            (128, 128, 128),  # Gray
            (112, 128, 144),  # Slate Gray
            (119, 136, 153)   # Light Slate Gray
        ]
        
        wall_colors = [
            (47, 79, 79),     # Dark Slate
            (72, 61, 139),    # Dark Slate Blue
            (47, 79, 79),     # Dark Slate Gray
            (84, 84, 84),     # Dark Gray
            (64, 64, 64),     # Darker Gray
            (32, 32, 32),     # Very Dark Gray
            (25, 25, 25),     # Almost Black
            (20, 20, 20)      # Very Dark
        ]
        
        # Randomly select colors
        self.floor_color = random.choice(floor_colors)
        self.wall_color = random.choice(wall_colors)
        
        # Ensure minimum contrast between floor and wall
        min_contrast = 50  # Minimum difference in brightness
        while True:
            # Calculate brightness (simple average of RGB)
            floor_brightness = sum(self.floor_color) / 3
            wall_brightness = sum(self.wall_color) / 3
            
            # If contrast is sufficient, break
            if abs(floor_brightness - wall_brightness) >= min_contrast:
                break
                
            # Otherwise, try new colors
            self.floor_color = random.choice(floor_colors)
            self.wall_color = random.choice(wall_colors)
        
    def _spawn_enemies(self, count):
        # On every 5th dungeon, spawn the boss in the exit room
        if self.current_level % 5 == 0:
            # Get the exit room position
            exit_room = self.dungeon_generator.exit_room
            if exit_room:
                # Spawn boss in the center of the exit room
                center_x = exit_room.x + exit_room.width // 2
                center_y = exit_room.y + exit_room.height // 2
                self.enemies.append(Enemy(center_x * self.tile_size, center_y * self.tile_size, 'boss'))
                # Spawn fewer regular enemies on boss floors
                count = max(2, count - 1)
        
        # Spawn regular enemies
        spawn_points = self.dungeon_generator.get_enemy_spawn_points(count)
        for x, y in spawn_points:
            # Skip if this is a boss floor and we're in the exit room
            if self.current_level % 5 == 0:
                exit_room = self.dungeon_generator.exit_room
                if exit_room and exit_room.rect.collidepoint(x, y):
                    continue
                    
            enemy_type = random.choice(['basic', 'fast', 'tank'])
            self.enemies.append(Enemy(x * self.tile_size, y * self.tile_size, enemy_type))
                
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state('menu')
            elif event.key == pygame.K_1:
                self.player.use_skill('skill1', self.enemies)
            elif event.key == pygame.K_2:
                self.player.use_skill('skill2', self.enemies)
            elif event.key == pygame.K_3:
                self.player.use_skill('skill3', self.enemies)
            elif event.key == pygame.K_4:
                self.player.use_skill('skill4', self.enemies)
            elif event.key == pygame.K_i:
                self.game.change_state('inventory')
            elif event.key == pygame.K_SPACE:
                self.player.dash()  # Trigger dash on spacebar
            elif event.key == pygame.K_u:  # Add 'U' key for using items
                # Use the first consumable item in inventory
                for item in self.player.inventory.items:
                    if item.get('type') == 'consumable':
                        if self.player.use_consumable(item):
                            self.player.inventory.remove_item(item)
                            break
                
    def update(self, dt):
        # Get keyboard input for movement
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        self.player.move(dx, dy, self.dungeon_grid, self.tile_size)
        
        # Update player
        self.player.update(dt)
        
        # Update shop cooldown
        if self.shop_cooldown > 0:
            self.shop_cooldown -= dt
        
        # Update attack arcs
        for arc in self.attack_arcs[:]:
            arc['duration'] -= dt
            arc['progress'] += dt / self.attack_animation_duration
            if arc['duration'] <= 0 or arc['progress'] >= 1:  # Remove when animation completes
                self.attack_arcs.remove(arc)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player, self.dungeon_grid, self.tile_size, self.enemies)
            
            # Check for enemy attacks
            if enemy.can_attack() and enemy.attack(self.player):
                self.player.take_damage(enemy.damage)
                
        # Remove dead enemies and handle drops
        new_enemies = []
        for enemy in self.enemies:
            if enemy.health > 0:
                new_enemies.append(enemy)
            else:
                # Handle drops
                drops = enemy.take_damage(0)  # This will return the drops
                if drops:
                    self.drops.extend(drops)
        self.enemies = new_enemies
        
        # Check for player attacks
        for enemy in self.enemies:
            if self.player.can_attack() and self.player.attack(enemy):
                # Create attack arc
                dx = enemy.x - self.player.x
                dy = enemy.y - self.player.y
                angle = math.atan2(dy, dx)
                self.attack_arcs.append({
                    'x': self.player.x,
                    'y': self.player.y,
                    'angle': angle,
                    'duration': 0.2,  # Duration of the attack arc visualization
                    'range': self.player.attack_range,
                    'progress': 0  # Animation progress
                })
                
                # Check all enemies within the arc
                for target in self.enemies:
                    # Calculate angle to target
                    target_dx = target.x - self.player.x
                    target_dy = target.y - self.player.y
                    target_angle = math.atan2(target_dy, target_dx)
                    
                    # Calculate angle difference (handling angle wrapping)
                    angle_diff = abs(target_angle - angle)
                    if angle_diff > math.pi:
                        angle_diff = 2 * math.pi - angle_diff
                    
                    # Check if target is within arc (45 degrees on each side)
                    if angle_diff <= math.pi/4:
                        # Check distance
                        distance = math.sqrt(target_dx * target_dx + target_dy * target_dy)
                        if distance <= self.player.attack_range:
                            # Apply damage and knockback
                            if target.take_damage(self.player.damage):
                                self.player.gain_experience(target.xp_value)
                            else:
                                # Apply knockback
                                knockback_x = math.cos(target_angle) * PLAYER_KNOCKBACK_FORCE
                                knockback_y = math.sin(target_angle) * PLAYER_KNOCKBACK_FORCE
                                target.knockback(knockback_x, knockback_y, PLAYER_KNOCKBACK_DURATION)
                
        # Update camera position to follow player - no bounds
        self.camera_x = self.player.x - self.screen_width // 2
        self.camera_y = self.player.y - self.screen_height // 2
        
        # Check for shop interaction
        shop_pos = self.dungeon_generator.get_shop_position()
        if shop_pos and self.shop_cooldown <= 0:  # Only check if cooldown is over
            shop_x, shop_y = shop_pos
            shop_rect = pygame.Rect(
                shop_x * self.tile_size - self.tile_size,
                shop_y * self.tile_size - self.tile_size,
                self.tile_size * 2,
                self.tile_size * 2
            )
            
            if self.player.rect.colliderect(shop_rect):
                self.game.change_state('shop')
                self.shop_cooldown = self.shop_cooldown_duration  # Start cooldown when entering shop
                
        # Check room type and handle accordingly
        current_room = self.dungeon_generator.get_room_at_position(
            self.player.x // self.tile_size,
            self.player.y // self.tile_size
        )
        
        if current_room:
            if current_room.room_type == 'exit':
                # Check if player is touching the exit square
                exit_size = self.tile_size * 4
                exit_x = current_room.x * self.tile_size + (current_room.width * self.tile_size - exit_size) // 2
                exit_y = current_room.y * self.tile_size + (current_room.height * self.tile_size - exit_size) // 2
                exit_rect = pygame.Rect(exit_x, exit_y, exit_size, exit_size)
                
                if self.player.rect.colliderect(exit_rect):
                    # Generate next level
                    self.current_level += 1
                    self.dungeon_grid = self.dungeon_generator.generate(self.current_level)
                    self._generate_dungeon_colors()  # Generate new colors for the new level
                    spawn_x, spawn_y = self.dungeon_generator.get_spawn_point()
                    self.player.x = spawn_x * self.tile_size
                    self.player.y = spawn_y * self.tile_size
                    self.enemies = []
                    self._spawn_enemies(5 + self.current_level)  # Increase enemies with level
                    # Reset camera position for new level
                    self.camera_x = self.player.x - self.screen_width // 2
                    self.camera_y = self.player.y - self.screen_height // 2
                    # Clear drops when changing levels
                    self.drops = []
                
            elif current_room.room_type == 'shop':
                # Enter shop
                self.game.change_state('shop')
                
        # Check for drops collection
        for drop in self.drops[:]:
            drop_rect = pygame.Rect(drop['x'], drop['y'], self.tile_size, self.tile_size)
            if self.player.rect.colliderect(drop_rect):
                if drop['type'] == 'gold':
                    self.player.inventory.add_gold(drop['amount'])
                elif drop['type'] == 'item':
                    self.player.inventory.add_item(drop['item'])
                self.drops.remove(drop)
                
        # Spawn new enemies if needed
        if len(self.enemies) < 3:
            self._spawn_enemies(1)
            
    def render(self, screen):
        # Clear screen
        screen.fill(BLACK)
        
        # Draw dungeon
        for y in range(self.dungeon_height):
            for x in range(self.dungeon_width):
                tile = self.dungeon_grid[y][x]
                if tile == 1:  # Floor
                    pygame.draw.rect(screen, self.floor_color, 
                        (x * self.tile_size - self.camera_x, 
                         y * self.tile_size - self.camera_y, 
                         self.tile_size, self.tile_size))
                elif tile == 2:  # Wall
                    pygame.draw.rect(screen, self.wall_color, 
                        (x * self.tile_size - self.camera_x, 
                         y * self.tile_size - self.camera_y, 
                         self.tile_size, self.tile_size))
                    
        # Draw stairs with emojis
        for stair_x, stair_y, direction in self.dungeon_generator.get_stair_positions():
            stair_rect = pygame.Rect(
                stair_x * self.tile_size - self.camera_x - self.tile_size//2,
                stair_y * self.tile_size - self.camera_y - self.tile_size//2,
                self.tile_size * 2,
                self.tile_size * 2
            )
            
            # Draw stair emoji
            font = pygame.font.SysFont('segoeuiemoji', self.tile_size * 2)
            stair_text = font.render('⬆️' if direction == 'up' else '⬇️', True, (255, 255, 255))
            text_rect = stair_text.get_rect(center=stair_rect.center)
            screen.blit(stair_text, text_rect)
            
        # Draw shop icon if on a shop floor
        shop_pos = self.dungeon_generator.get_shop_position()
        if shop_pos:
            shop_x, shop_y = shop_pos
            shop_rect = pygame.Rect(
                shop_x * self.tile_size - self.camera_x - self.tile_size,
                shop_y * self.tile_size - self.camera_y - self.tile_size,
                self.tile_size * 2,
                self.tile_size * 2
            )
            
            # Draw shop icon using emoji
            font = pygame.font.SysFont('segoeuiemoji', self.tile_size * 2)
            shop_text = font.render('💰', True, (255, 255, 255))
            text_rect = shop_text.get_rect(center=shop_rect.center)
            screen.blit(shop_text, text_rect)
            
        # Draw boss room if on a boss floor
        if self.current_level % 5 == 0:
            boss_room = self.dungeon_generator.get_boss_room()
            if boss_room:
                # Draw boss room outline
                boss_rect = pygame.Rect(
                    boss_room.x * self.tile_size - self.camera_x,
                    boss_room.y * self.tile_size - self.camera_y,
                    boss_room.width * self.tile_size,
                    boss_room.height * self.tile_size
                )
                pygame.draw.rect(screen, (139, 0, 139), boss_rect, 3)  # Purple outline
                
                # Draw boss icon in center
                boss_icon_rect = pygame.Rect(
                    (boss_room.x + boss_room.width//2) * self.tile_size - self.camera_x - self.tile_size,
                    (boss_room.y + boss_room.height//2) * self.tile_size - self.camera_y - self.tile_size,
                    self.tile_size * 2,
                    self.tile_size * 2
                )
                
                # Draw boss emoji
                font = pygame.font.SysFont('segoeuiemoji', self.tile_size * 2)
                boss_text = font.render('👾', True, (255, 255, 255))
                text_rect = boss_text.get_rect(center=boss_icon_rect.center)
                screen.blit(boss_text, text_rect)
            
        # Draw drops
        for drop in self.drops:
            if drop['type'] == 'gold':
                # Draw gold coin
                pygame.draw.circle(screen, YELLOW,
                    (int(drop['x'] - self.camera_x + self.tile_size//2),
                     int(drop['y'] - self.camera_y + self.tile_size//2)),
                    self.tile_size//4)
            elif drop['type'] == 'item':
                # Draw item box
                pygame.draw.rect(screen, GREEN,
                    (drop['x'] - self.camera_x,
                     drop['y'] - self.camera_y,
                     self.tile_size, self.tile_size))
            
        # Draw attack arcs
        for arc in self.attack_arcs:
            # Calculate base angles
            base_angle = arc['angle']
            arc_width = math.pi/6  # Reduced from pi/4 to pi/6 for a narrower arc
            
            # Create a left-to-right swipe effect
            if arc['progress'] < 1:
                # Calculate the current arc position
                # Start from left side and move to right
                start_offset = -arc_width * (1 - arc['progress'])  # Moves from -30 to 0
                end_offset = arc_width * arc['progress']  # Moves from 0 to 30
                
                current_start = base_angle + start_offset
                current_end = base_angle + end_offset
                
                # Add trail effect
                trail_progress = max(0, arc['progress'] - 0.1)  # Trail starts after 10% of the animation
                if trail_progress > 0:
                    # Calculate trail angles
                    trail_start = current_start - arc_width * (1 - trail_progress)
                    trail_end = current_start
                    
                    # Draw trail
                    trail_points = []
                    center_x = arc['x'] - self.camera_x
                    center_y = arc['y'] - self.camera_y
                    trail_points.append((center_x, center_y))
                    
                    for angle in range(int(math.degrees(trail_start)), int(math.degrees(trail_end)) + 1):
                        rad = math.radians(angle)
                        x = center_x + math.cos(rad) * arc['range'] * 0.8  # Shorter trail
                        y = center_y + math.sin(rad) * arc['range'] * 0.8
                        trail_points.append((x, y))
                    
                    if len(trail_points) > 2:
                        # Draw trail with reduced opacity
                        pygame.draw.polygon(screen, self.attack_colors['trail'], trail_points)
                        pygame.draw.lines(screen, self.attack_colors['trail'], True, trail_points, 1)
            
            # Draw main attack arc
            points = []
            center_x = arc['x'] - self.camera_x
            center_y = arc['y'] - self.camera_y
            
            # Add center point
            points.append((center_x, center_y))
            
            # Add arc points
            for angle in range(int(math.degrees(current_start)), int(math.degrees(current_end)) + 1):
                rad = math.radians(angle)
                x = center_x + math.cos(rad) * arc['range']
                y = center_y + math.sin(rad) * arc['range']
                points.append((x, y))
            
            # Draw filled arc with effects
            if len(points) > 2:
                # Draw main arc with reduced opacity
                pygame.draw.polygon(screen, self.attack_colors['primary'], points)
                # Draw inner highlight with reduced opacity
                inner_points = []
                for x, y in points[1:]:  # Skip center point
                    dx = x - center_x
                    dy = y - center_y
                    inner_x = center_x + dx * 0.8
                    inner_y = center_y + dy * 0.8
                    inner_points.append((inner_x, inner_y))
                if len(inner_points) > 2:
                    pygame.draw.polygon(screen, self.attack_colors['secondary'], inner_points)
                # Draw outline with reduced opacity
                pygame.draw.lines(screen, self.attack_colors['primary'], True, points, 1)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen, self.camera_x, self.camera_y)
            
        # Draw player
        self.player.draw(screen, self.camera_x, self.camera_y)
        
        # Draw UI
        self._draw_ui(screen)
        
    def _draw_ui(self, screen):
        # Create semi-transparent surface for UI
        ui_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        # Draw health bar
        health_rect = pygame.Rect(UI_PADDING, UI_PADDING, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        health_fill = pygame.Rect(UI_PADDING, UI_PADDING, 
                                (self.player.health / self.player.max_health) * HEALTH_BAR_WIDTH, 
                                HEALTH_BAR_HEIGHT)
        
        # Health bar background
        pygame.draw.rect(ui_surface, (64, 64, 64, 192), health_rect)
        # Health bar fill
        pygame.draw.rect(ui_surface, (255, 0, 0, 192), health_fill)
        # Health bar border
        pygame.draw.rect(ui_surface, (255, 255, 255, 192), health_rect, 2)
        
        # Health text with emoji
        font = pygame.font.SysFont('segoeuiemoji', 20)
        health_text = font.render(f"❤️ HP: {int(self.player.health)}/{self.player.max_health}", True, WHITE)
        ui_surface.blit(health_text, (UI_PADDING + 5, UI_PADDING + 2))
        
        # Draw mana bar
        mana_rect = pygame.Rect(UI_PADDING, UI_PADDING + HEALTH_BAR_HEIGHT + 5, MANA_BAR_WIDTH, MANA_BAR_HEIGHT)
        mana_fill = pygame.Rect(UI_PADDING, UI_PADDING + HEALTH_BAR_HEIGHT + 5,
                              (self.player.mana / self.player.max_mana) * MANA_BAR_WIDTH,
                              MANA_BAR_HEIGHT)
        
        # Mana bar background
        pygame.draw.rect(ui_surface, (64, 64, 64, 192), mana_rect)
        # Mana bar fill
        pygame.draw.rect(ui_surface, (0, 0, 255, 192), mana_fill)
        # Mana bar border
        pygame.draw.rect(ui_surface, (255, 255, 255, 192), mana_rect, 2)
        
        # Mana text with emoji
        mana_text = font.render(f"💧 MP: {int(self.player.mana)}/{self.player.max_mana}", True, WHITE)
        ui_surface.blit(mana_text, (UI_PADDING + 5, UI_PADDING + HEALTH_BAR_HEIGHT + 7))
        
        # Draw stats panel
        stats_panel = pygame.Rect(UI_PADDING, UI_PADDING + HEALTH_BAR_HEIGHT + MANA_BAR_HEIGHT + 10,
                                200, 100)
        pygame.draw.rect(ui_surface, (64, 64, 64, 192), stats_panel)
        pygame.draw.rect(ui_surface, (255, 255, 255, 192), stats_panel, 2)
        
        # Stats text with emojis
        level_text = font.render(f"⭐ Level: {self.player.level}", True, WHITE)
        xp_text = font.render(f"✨ XP: {self.player.experience}/{self.player.experience_to_next_level}", True, WHITE)
        dungeon_text = font.render(f"🏰 Dungeon: {self.current_level}", True, WHITE)
        gold_text = font.render(f"💰 Gold: {self.player.inventory.gold}", True, (255, 215, 0))
        
        ui_surface.blit(level_text, (UI_PADDING + 5, stats_panel.y + 5))
        ui_surface.blit(xp_text, (UI_PADDING + 5, stats_panel.y + 25))
        ui_surface.blit(dungeon_text, (UI_PADDING + 5, stats_panel.y + 45))
        ui_surface.blit(gold_text, (UI_PADDING + 5, stats_panel.y + 65))
        
        # Draw skills panel
        skills_panel = pygame.Rect(WINDOW_WIDTH - 220, WINDOW_HEIGHT - 120, 200, 100)
        pygame.draw.rect(ui_surface, (64, 64, 64, 192), skills_panel)
        pygame.draw.rect(ui_surface, (255, 255, 255, 192), skills_panel, 2)
        
        # Draw skills with emojis
        skill_emojis = {
            'Fireball': '🔥',
            'Ice Nova': '❄️',
            'Lightning Strike': '⚡',
            'Heal': '💚'
        }
        
        for i, (skill_name, skill) in enumerate(self.player.skills.items()):
            x = skills_panel.x + 10 + (i * 45)
            y = skills_panel.y + 10
            
            # Skill icon background
            icon_rect = pygame.Rect(x, y, 40, 40)
            pygame.draw.rect(ui_surface, (32, 32, 32, 192), icon_rect)
            pygame.draw.rect(ui_surface, (255, 255, 255, 192), icon_rect, 2)
            
            # Draw skill emoji
            skill_text = font.render(skill_emojis[skill['name']], True, (255, 255, 255))
            text_rect = skill_text.get_rect(center=icon_rect.center)
            ui_surface.blit(skill_text, text_rect)
            
            # Cooldown overlay
            if skill['current_cooldown'] > 0:
                cooldown_height = (skill['current_cooldown'] / skill['cooldown']) * 40
                cooldown_rect = pygame.Rect(x, y + 40 - cooldown_height, 40, cooldown_height)
                pygame.draw.rect(ui_surface, (0, 0, 0, 128), cooldown_rect)
                
            # Skill number
            number_text = font.render(str(i + 1), True, WHITE)
            ui_surface.blit(number_text, (x + 5, y + 5))
            
        # Draw the UI surface
        screen.blit(ui_surface, (0, 0)) 