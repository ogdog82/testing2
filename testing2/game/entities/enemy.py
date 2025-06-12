import pygame
import math
import random
from ..constants import (
    ENEMY_SPEED, ENEMY_HEALTH, ENEMY_DAMAGE,
    ENEMY_ATTACK_RANGE, ENEMY_ATTACK_SPEED,
    ENEMY_DETECTION_RANGE
)
from ..items.item_system import ItemSystem

class Enemy:
    def __init__(self, x, y, enemy_type='basic'):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.speed = ENEMY_SPEED
        self.health = ENEMY_HEALTH
        self.max_health = ENEMY_HEALTH
        self.damage = ENEMY_DAMAGE
        self.attack_range = ENEMY_ATTACK_RANGE
        self.detection_range = ENEMY_DETECTION_RANGE
        self.attack_speed = ENEMY_ATTACK_SPEED
        self.attack_cooldown = 0
        self.direction = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.enemy_type = enemy_type
        self.path = []  # For storing path to player
        self.path_update_cooldown = 0
        self.item_system = ItemSystem()
        
        # Knockback
        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_duration = 0
        
        # Status effects
        self.burn_duration = 0
        self.burn_damage = 0
        self.slow_duration = 0
        self.chain_lightning = False
        self.chain_damage = 0
        self.chain_targets = 0
        self.base_speed = self.speed  # Store base speed for slow effect
        
        # Enemy type modifiers
        if enemy_type == 'fast':
            self.speed *= 1.5
            self.health *= 0.7
            self.damage *= 0.5  # Reduced damage
            self.attack_speed *= 2.5  # Much faster attacks
            self.detection_range *= 1.2
            self.xp_value = 10  # More XP for faster enemies
        elif enemy_type == 'tank':
            self.speed *= 0.7
            self.health *= 2
            self.damage *= 2.5  # Much higher damage
            self.attack_speed *= 0.4  # Much slower attacks
            self.detection_range *= 0.8
            self.xp_value = 25  # More XP for tanky enemies
        elif enemy_type == 'boss':
            self.speed *= 0.8
            self.health *= 5
            self.damage *= 3
            self.attack_speed *= 0.6  # Slower attacks but not as slow as tank
            self.detection_range *= 1.5
            self.width = 64
            self.height = 64
            self.rect = pygame.Rect(x, y, self.width, self.height)
            self.xp_value = 100  # Much more XP for bosses
        else:  # basic enemy
            self.xp_value = 15  # Base XP value
        
    def knockback(self, force_x, force_y, duration):
        self.knockback_x = force_x
        self.knockback_y = force_y
        self.knockback_duration = duration
        
    def update(self, dt, player, dungeon_grid, tile_size, enemies):
        # Update knockback
        if self.knockback_duration > 0:
            # Calculate new position with knockback
            new_x = self.x + self.knockback_x * dt
            new_y = self.y + self.knockback_y * dt
            
            # Create temporary rect for collision detection
            temp_rect = self.rect.copy()
            temp_rect.x = new_x
            temp_rect.y = new_y
            
            # Check for wall collisions
            grid_x = int(new_x // tile_size)
            grid_y = int(new_y // tile_size)
            
            can_move = True
            # Check surrounding tiles for walls
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    check_x = grid_x + dx
                    check_y = grid_y + dy
                    
                    if (0 <= check_x < len(dungeon_grid[0]) and 
                        0 <= check_y < len(dungeon_grid) and 
                        dungeon_grid[check_y][check_x] == 2):  # Wall tile
                        
                        wall_rect = pygame.Rect(
                            check_x * tile_size,
                            check_y * tile_size,
                            tile_size,
                            tile_size
                        )
                        
                        if temp_rect.colliderect(wall_rect):
                            can_move = False
                            # Stop knockback when hitting a wall
                            self.knockback_duration = 0
                            break
                            
            # Check collisions with other enemies
            for other in enemies:
                if other != self and temp_rect.colliderect(other.rect):
                    can_move = False
                    # Stop knockback when hitting another enemy
                    self.knockback_duration = 0
                    break
            
            # Check collision with player
            if temp_rect.colliderect(player.rect):
                can_move = False
                # Stop knockback when hitting player
                self.knockback_duration = 0
                            
            if can_move:
                self.x = new_x
                self.y = new_y
                self.rect.x = self.x
                self.rect.y = self.y
                
            self.knockback_duration -= dt
            return  # Skip normal movement during knockback
            
        # Update status effects
        if self.burn_duration > 0:
            self.burn_duration -= dt
            self.take_damage(self.burn_damage * dt)  # Apply burn damage per second
            
        if self.slow_duration > 0:
            self.slow_duration -= dt
            if self.slow_duration <= 0:
                self.speed = self.base_speed  # Restore speed when slow ends
                
        if self.chain_lightning and self.chain_targets > 0:
            # Find closest enemy to chain to
            closest_enemy = None
            min_distance = float('inf')
            for enemy in enemies:
                if enemy != self:
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance < min_distance:
                        min_distance = distance
                        closest_enemy = enemy
                        
            if closest_enemy and min_distance <= 100:  # Chain range
                closest_enemy.take_damage(self.chain_damage)
                self.chain_targets -= 1
                if self.chain_targets <= 0:
                    self.chain_lightning = False
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Only move if player is within detection range
        if distance <= self.detection_range:
            # Move directly towards player
            if distance > 0:
                self.direction.x = dx / distance
                self.direction.y = dy / distance
                
            # Try to move
            new_x = self.x + self.direction.x * self.speed
            new_y = self.y + self.direction.y * self.speed
            
            # Create temporary rect for collision detection
            temp_rect = self.rect.copy()
            temp_rect.x = new_x
            temp_rect.y = new_y
            
            # Check for wall collisions
            grid_x = int(new_x // tile_size)
            grid_y = int(new_y // tile_size)
            
            can_move = True
            # Check surrounding tiles for walls
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    check_x = grid_x + dx
                    check_y = grid_y + dy
                    
                    if (0 <= check_x < len(dungeon_grid[0]) and 
                        0 <= check_y < len(dungeon_grid) and 
                        dungeon_grid[check_y][check_x] == 2):  # Wall tile
                        
                        wall_rect = pygame.Rect(
                            check_x * tile_size,
                            check_y * tile_size,
                            tile_size,
                            tile_size
                        )
                        
                        if temp_rect.colliderect(wall_rect):
                            can_move = False
                            # Try to slide along wall
                            if abs(self.direction.x) > abs(self.direction.y):
                                # Try vertical movement
                                temp_rect.x = self.x
                                temp_rect.y = new_y
                                if not any(temp_rect.colliderect(pygame.Rect(
                                    (grid_x + dx) * tile_size,
                                    (grid_y + dy) * tile_size,
                                    tile_size,
                                    tile_size
                                )) for dy in [-1, 0, 1] for dx in [-1, 0, 1] 
                                if 0 <= grid_x + dx < len(dungeon_grid[0]) 
                                and 0 <= grid_y + dy < len(dungeon_grid) 
                                and dungeon_grid[grid_y + dy][grid_x + dx] == 2):
                                    self.y = new_y
                            else:
                                # Try horizontal movement
                                temp_rect.x = new_x
                                temp_rect.y = self.y
                                if not any(temp_rect.colliderect(pygame.Rect(
                                    (grid_x + dx) * tile_size,
                                    (grid_y + dy) * tile_size,
                                    tile_size,
                                    tile_size
                                )) for dy in [-1, 0, 1] for dx in [-1, 0, 1] 
                                if 0 <= grid_x + dx < len(dungeon_grid[0]) 
                                and 0 <= grid_y + dy < len(dungeon_grid) 
                                and dungeon_grid[grid_y + dy][grid_x + dx] == 2):
                                    self.x = new_x
                            break
            
            # Check collisions with other enemies
            for other in enemies:
                if other != self and temp_rect.colliderect(other.rect):
                    can_move = False
                    # Instead of pushing, just stop movement
                    break
            
            # Check collision with player
            if temp_rect.colliderect(player.rect):
                can_move = False
                # Instead of pushing, just stop movement
                            
            if can_move:
                self.x = new_x
                self.y = new_y
                self.rect.x = self.x
                self.rect.y = self.y
        else:
            self.direction.x = 0
            self.direction.y = 0
            
    def _update_path(self, player, dungeon_grid, tile_size):
        # Simple pathfinding: move towards player while avoiding walls
        start_x = int(self.x // tile_size)
        start_y = int(self.y // tile_size)
        end_x = int(player.x // tile_size)
        end_y = int(player.y // tile_size)
        
        # Use A* pathfinding or simple wall avoidance
        # For now, use a simple approach: try to move in the general direction of the player
        path = []
        current_x, current_y = start_x, start_y
        
        while (current_x, current_y) != (end_x, end_y):
            # Calculate direction to player
            dx = end_x - current_x
            dy = end_y - current_y
            
            # Try to move in x direction first
            if dx != 0:
                next_x = current_x + (1 if dx > 0 else -1)
                if (0 <= next_x < len(dungeon_grid[0]) and 
                    dungeon_grid[current_y][next_x] != 2):  # Not a wall
                    current_x = next_x
                    path.append((current_x, current_y))
                    continue
                    
            # Try to move in y direction
            if dy != 0:
                next_y = current_y + (1 if dy > 0 else -1)
                if (0 <= next_y < len(dungeon_grid) and 
                    dungeon_grid[next_y][current_x] != 2):  # Not a wall
                    current_y = next_y
                    path.append((current_x, current_y))
                    continue
                    
            # If we can't move in either direction, try diagonal
            if dx != 0 and dy != 0:
                next_x = current_x + (1 if dx > 0 else -1)
                next_y = current_y + (1 if dy > 0 else -1)
                if (0 <= next_x < len(dungeon_grid[0]) and 
                    0 <= next_y < len(dungeon_grid) and 
                    dungeon_grid[next_y][next_x] != 2):  # Not a wall
                    current_x = next_x
                    current_y = next_y
                    path.append((current_x, current_y))
                    continue
                    
            # If we can't find a path, break
            break
            
        self.path = path
        
    def can_attack(self):
        return self.attack_cooldown <= 0
        
    def attack(self, player):
        if not self.can_attack():
            return False
            
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance <= self.attack_range:
            self.attack_cooldown = 1.0 / self.attack_speed
            # Don't move during attack
            self.direction.x = 0
            self.direction.y = 0
            return True
        return False
        
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            return self._generate_drops()
        return False
        
    def _generate_drops(self):
        """Generate drops when enemy dies."""
        drops = []
        
        # Determine drop chances based on enemy type
        if self.enemy_type == 'boss':
            gold_chance = 1.0  # Always drop gold
            item_chance = 0.8  # 80% chance for item
            gold_amount = random.randint(50, 100)
            item_rarity = 'legendary'  # Bosses drop legendary items
        elif self.enemy_type == 'tank':
            gold_chance = 0.5  # 50% chance for gold
            item_chance = 0.3  # 30% chance for item
            gold_amount = random.randint(20, 40)
            item_rarity = 'rare'  # Tanks drop rare items
        elif self.enemy_type == 'fast':
            gold_chance = 0.4  # 40% chance for gold
            item_chance = 0.2  # 20% chance for item
            gold_amount = random.randint(10, 25)
            item_rarity = 'uncommon'  # Fast enemies drop uncommon items
        else:  # basic enemy
            gold_chance = 0.3  # 30% chance for gold
            item_chance = 0.1  # 10% chance for item
            gold_amount = random.randint(5, 15)
            item_rarity = 'common'  # Basic enemies drop common items
            
        # Generate gold drop
        if random.random() < gold_chance:
            drops.append({
                'type': 'gold',
                'amount': gold_amount,
                'x': self.x,
                'y': self.y
            })
            
        # Generate item drop
        if random.random() < item_chance:
            item = self.item_system.generate_item(rarity=item_rarity)
            if item:
                drops.append({
                    'type': 'item',
                    'item': item,
                    'x': self.x,
                    'y': self.y
                })
                
        return drops
        
    def draw(self, screen, camera_x=0, camera_y=0):
        # Draw enemy using emoji
        font = pygame.font.SysFont('segoeuiemoji', 32)  # Use emoji font
        
        # Choose emoji based on enemy type
        if self.enemy_type == 'boss':
            emoji = '👾'  # Boss enemy
        elif self.enemy_type == 'fast':
            emoji = '👻'  # Fast enemy
        elif self.enemy_type == 'tank':
            emoji = '🦖'  # Tank enemy
        else:
            emoji = '👹'  # Basic enemy
            
        # Draw the emoji
        text = font.render(emoji, True, (255, 255, 255))
        screen.blit(text, (self.x - camera_x, self.y - camera_y))
        
        # Draw health bar - single red bar
        health_percentage = self.health / self.max_health
        health_width = 32  # Fixed width for all enemies
        health_height = 4  # Thinner health bar
        
        # Draw current health (bright red)
        current_health_width = int(health_width * health_percentage)
        if current_health_width > 0:  # Only draw if there's health left
            pygame.draw.rect(screen, (255, 0, 0), 
                (self.x - camera_x, self.y - camera_y - 8, current_health_width, health_height))
        
        # Draw status effect indicators
        if self.burn_duration > 0:
            # Draw fire effect
            fire_text = font.render('🔥', True, (255, 255, 255))
            screen.blit(fire_text, (self.x - camera_x + self.width//2, self.y - camera_y - 15))
                
        if self.slow_duration > 0:
            # Draw ice effect
            ice_text = font.render('❄️', True, (255, 255, 255))
            screen.blit(ice_text, (self.x - camera_x + self.width//2 + 8, self.y - camera_y - 15))
                
        if self.chain_lightning:
            # Draw lightning effect
            lightning_text = font.render('⚡', True, (255, 255, 255))
            screen.blit(lightning_text, (self.x - camera_x + self.width//2 - 8, self.y - camera_y - 15))
        
        # Draw detection range (for debugging)
        # pygame.draw.circle(screen, (255, 255, 255, 32), (int(self.x + self.width/2), int(self.y + self.height/2)), self.detection_range, 1) 