import pygame
import math
import random
from ..constants import (
    PLAYER_SPEED, PLAYER_HEALTH, PLAYER_MANA,
    PLAYER_ATTACK_RANGE, PLAYER_ATTACK_SPEED,
    AUTO_ATTACK_DAMAGE, PLAYER_KNOCKBACK_FORCE, PLAYER_KNOCKBACK_DURATION
)
from .inventory import Inventory
from ..items.item_system import ItemSystem

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.mana = PLAYER_MANA
        self.max_mana = PLAYER_MANA
        self.damage = AUTO_ATTACK_DAMAGE  # Initialize base damage
        self.attack_range = PLAYER_ATTACK_RANGE
        self.attack_speed = PLAYER_ATTACK_SPEED
        self.attack_cooldown = 0
        self.direction = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        self.gold = 0
        
        # Initialize fonts
        self.font_small = pygame.font.SysFont('segoeuiemoji', 20)
        self.font_medium = pygame.font.SysFont('segoeuiemoji', 24)
        self.font_large = pygame.font.SysFont('segoeuiemoji', 32)
        
        # Dash properties
        self.dash_cooldown = 0
        self.dash_duration = 0.1  # Duration of dash in seconds
        self.dash_speed = 20  # Dash speed multiplier
        self.dash_active = False
        self.dash_direction = pygame.math.Vector2(0, 0)
        self.dash_poofs = []  # List to store dash poof effects
        
        # Skills with effects
        self.skills = {
            'skill1': {
                'name': 'Fireball',
                'cooldown': 5,
                'current_cooldown': 0,
                'mana_cost': 20,
                'damage': 30,
                'range': 150,
                'effect': 'fire'
            },
            'skill2': {
                'name': 'Ice Nova',
                'cooldown': 8,
                'current_cooldown': 0,
                'mana_cost': 30,
                'damage': 25,
                'range': 100,
                'effect': 'ice'
            },
            'skill3': {
                'name': 'Lightning Strike',
                'cooldown': 12,
                'current_cooldown': 0,
                'mana_cost': 40,
                'damage': 50,
                'range': 200,
                'effect': 'lightning'
            },
            'skill4': {
                'name': 'Heal',
                'cooldown': 20,
                'current_cooldown': 0,
                'mana_cost': 50,
                'heal_amount': 50,
                'effect': 'heal'
            }
        }
        
        # Stats
        self.stats = {
            'strength': 10,
            'dexterity': 10,
            'intelligence': 10,
            'vitality': 10
        }
        
        # Equipment slots
        self.equipment = {
            'weapon': None,
            'armor': None,
            'accessory': None
        }
        
        # Inventory
        self.inventory = Inventory()
        self.item_system = ItemSystem()
        
        # Update stats based on equipment
        self._update_stats()
        
    def move(self, dx, dy, dungeon_grid, tile_size):
        # Store original position
        original_x = self.x
        original_y = self.y
        
        # Handle dash movement
        if self.dash_active:
            # Calculate new position
            new_x = self.x + self.dash_direction.x * self.dash_speed
            new_y = self.y + self.dash_direction.y * self.dash_speed
            
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
                            self.dash_active = False  # Stop dash when hitting wall
                            break
                            
            if can_move:
                self.x = new_x
                self.y = new_y
                self.rect.x = self.x
                self.rect.y = self.y
                
                # Add poof effect
                if random.random() < 0.3:  # Reduced from 0.5 to 0.3 for fewer poofs
                    self.dash_poofs.append({
                        'x': self.x,
                        'y': self.y,
                        'duration': 0.2,
                        'opacity': 255
                    })
            else:
                self.dash_active = False  # Stop dash if can't move
        else:
            # Normal movement
            if dx != 0 or dy != 0:
                # Normalize direction
                length = math.sqrt(dx * dx + dy * dy)
                if length > 0:
                    dx /= length
                    dy /= length
                    self.direction.x = dx
                    self.direction.y = dy
                
                # Calculate new position
                new_x = self.x + dx * self.speed
                new_y = self.y + dy * self.speed
                
                # Create temporary rect for collision detection
                temp_rect = self.rect.copy()
                temp_rect.x = new_x
                temp_rect.y = new_y
                
                # Check for wall collisions
                grid_x = int(new_x // tile_size)
                grid_y = int(new_y // tile_size)
                
                can_move_x = True
                can_move_y = True
                
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
                                # Try to slide along walls
                                if abs(dx) > abs(dy):
                                    can_move_x = False
                                else:
                                    can_move_y = False
                                    
                # Apply movement
                if can_move_x:
                    self.x = new_x
                if can_move_y:
                    self.y = new_y
                    
                self.rect.x = self.x
                self.rect.y = self.y
        
    def update(self, dt):
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # Update dash cooldown
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
            
        # Update dash duration
        if self.dash_active:
            self.dash_duration -= dt
            if self.dash_duration <= 0:
                self.dash_active = False
                # Add final poof effect
                self.dash_poofs.append({
                    'x': self.rect.centerx,
                    'y': self.rect.centery,
                    'opacity': 255
                })
                
        # Update dash poofs
        for poof in self.dash_poofs[:]:
            poof['opacity'] -= 255 * dt  # Fade out over 1 second
            if poof['opacity'] <= 0:
                self.dash_poofs.remove(poof)
                
        # Update skills cooldowns
        for skill in self.skills.values():
            if skill['cooldown'] > 0:
                skill['cooldown'] -= dt
                
        # Regenerate mana
        self.mana = min(self.max_mana, self.mana + 1 * dt)
                
    def can_attack(self):
        return self.attack_cooldown <= 0
        
    def attack(self, target):
        if not self.can_attack():
            return False
            
        # Handle both coordinate-based and enemy-based attacks
        if isinstance(target, tuple):
            # Coordinate-based attack
            target_x, target_y = target
            dx = target_x - self.x
            dy = target_y - self.y
        else:
            # Enemy-based attack
            dx = target.x - self.x
            dy = target.y - self.y
            
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance <= self.attack_range:
            self.attack_cooldown = 1.0 / self.attack_speed
            
            # Calculate attack angle
            attack_angle = math.atan2(dy, dx)
            
            # Apply knockback to the target
            if not isinstance(target, tuple):
                knockback_x = math.cos(attack_angle) * PLAYER_KNOCKBACK_FORCE
                knockback_y = math.sin(attack_angle) * PLAYER_KNOCKBACK_FORCE
                target.knockback(knockback_x, knockback_y, PLAYER_KNOCKBACK_DURATION)
            
            return True
        return False
        
    def use_skill(self, skill_name, enemies=None):
        if skill_name not in self.skills:
            return False
            
        skill = self.skills[skill_name]
        if skill['current_cooldown'] <= 0 and self.mana >= skill['mana_cost']:
            self.mana -= skill['mana_cost']
            skill['current_cooldown'] = skill['cooldown']
            
            # Apply skill effects
            if skill['effect'] == 'heal':
                self.heal(skill['heal_amount'])
            elif skill['effect'] in ['fire', 'ice', 'lightning'] and enemies:
                # Get all enemies in range
                for enemy in enemies:
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance <= skill['range']:
                        # Apply damage
                        enemy.take_damage(skill['damage'])
                        
                        # Apply additional effects based on skill type
                        if skill['effect'] == 'fire':
                            # Fire damage over time
                            enemy.burn_duration = 3.0  # 3 seconds
                            enemy.burn_damage = skill['damage'] * 0.2  # 20% of initial damage
                        elif skill['effect'] == 'ice':
                            # Slow effect
                            enemy.speed *= 0.5  # 50% slow
                            enemy.slow_duration = 2.0  # 2 seconds
                        elif skill['effect'] == 'lightning':
                            # Chain lightning effect
                            enemy.chain_lightning = True
                            enemy.chain_damage = skill['damage'] * 0.5  # 50% of initial damage
                            enemy.chain_targets = 2  # Can hit 2 additional targets
                
            return True
        return False
        
    def take_damage(self, amount):
        # Apply damage reduction from stats and equipment
        damage_reduction = self.stats['vitality'] * 0.5
        if self.equipment['armor']:
            damage_reduction += self.equipment['armor'].get('defense', 0)
            
        actual_damage = max(1, amount - damage_reduction)
        self.health = max(0, self.health - actual_damage)
        return self.health <= 0
        
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        
    def restore_mana(self, amount):
        self.mana = min(self.max_mana, self.mana + amount)
        
    def gain_experience(self, amount):
        self.experience += amount
        while self.experience >= self.experience_to_next_level:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        
        # Increase stats
        self.stats['strength'] += 2
        self.stats['dexterity'] += 2
        self.stats['intelligence'] += 2
        self.stats['vitality'] += 2
        
        # Increase max health and mana
        self.max_health += 20
        self.max_mana += 10
        self.health = self.max_health
        self.mana = self.max_mana
        
        # Increase base damage
        self.damage = AUTO_ATTACK_DAMAGE + (self.stats['strength'] * 0.5)
        
    def add_to_inventory(self, item):
        if len(self.inventory) < self.inventory_size:
            self.inventory.append(item)
            return True
        return False
        
    def equip_item(self, item):
        if item['type'] in self.equipment:
            # Unequip current item if any
            if self.equipment[item['type']]:
                self.inventory.add_item(self.equipment[item['type']])
            self.equipment[item['type']] = item
            self.inventory.remove_item(item)
            
            # Update player stats based on equipped items
            self._update_stats()
            return True
        return False
        
    def unequip_item(self, slot):
        """Unequip an item from the specified slot."""
        if slot in self.equipment and self.equipment[slot]:
            # Add the item back to inventory
            if self.inventory.add_item(self.equipment[slot]):
                # Clear the equipment slot
                self.equipment[slot] = None
                # Update player stats
                self._update_stats()
                return True
        return False
        
    def _update_stats(self):
        # Get base stats
        self.stats = {
            'strength': 10 + (self.level - 1) * 2,
            'dexterity': 10 + (self.level - 1) * 2,
            'intelligence': 10 + (self.level - 1) * 2,
            'vitality': 10 + (self.level - 1) * 2
        }
        
        # Add equipment stats
        equipped_stats = self.inventory.get_equipped_stats()
        for stat, value in equipped_stats.items():
            if stat in self.stats:
                self.stats[stat] += value
                
        # Update derived stats
        self.max_health = PLAYER_HEALTH + (self.stats['vitality'] * 5)
        self.max_mana = PLAYER_MANA + (self.stats['intelligence'] * 3)
        self.damage = AUTO_ATTACK_DAMAGE + (self.stats['strength'] * 0.5)
        if self.equipment['weapon']:
            self.damage += self.equipment['weapon'].get('damage', 0)
            
        # Ensure current health/mana don't exceed max
        self.health = min(self.health, self.max_health)
        self.mana = min(self.mana, self.max_mana)
        
    def use_consumable(self, item):
        if item.get('type') == 'consumable':
            # Apply consumable effects
            if 'heal' in item:
                self.heal(item['heal'])
            if 'mana' in item:
                self.restore_mana(item['mana'])
            # Remove the item after use
            self.inventory.remove_item(item)
            return True
        return False
        
    def draw(self, screen, camera_x=0, camera_y=0):
        # Draw dash poofs
        for poof in self.dash_poofs:
            poof_surface = self.font_small.render('💨', True, (255, 255, 255))
            poof_surface.set_alpha(int(poof['opacity']))
            poof_rect = poof_surface.get_rect(center=(poof['x'] - camera_x, poof['y'] - camera_y))
            screen.blit(poof_surface, poof_rect)
            
        # Draw player using emoji
        player_text = self.font_large.render('🧙', True, (255, 255, 255))
        screen.blit(player_text, (self.x - camera_x, self.y - camera_y))
        
        # Draw health bar
        health_width = 32
        health_height = 4
        health_x = self.rect.x + (self.rect.width - health_width) // 2
        health_y = self.rect.y - 10
        pygame.draw.rect(screen, (100, 0, 0), (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, (255, 0, 0), (health_x, health_y, health_width * (self.health / self.max_health), health_height))
        
        # Draw mana bar
        mana_width = 32
        mana_height = 4
        mana_x = self.rect.x + (self.rect.width - mana_width) // 2
        mana_y = self.rect.y - 5
        pygame.draw.rect(screen, (0, 0, 100), (mana_x, mana_y, mana_width, mana_height))
        pygame.draw.rect(screen, (0, 0, 255), (mana_x, mana_y, mana_width * (self.mana / self.max_mana), mana_height))
        
        # Draw level
        font = pygame.font.SysFont('segoeuiemoji', 24)
        level_text = font.render(f"Lvl {self.level}", True, (255, 255, 255))
        screen.blit(level_text, (self.x - camera_x, self.y - camera_y - 25))
        
    def dash(self):
        # Check if dash is available
        if self.dash_cooldown <= 0:
            # Calculate dash cooldown based on dexterity
            base_cooldown = 2.0  # Base cooldown of 2 seconds
            dexterity_reduction = self.stats.get('dexterity', 0) * 0.1  # 0.1s reduction per point
            self.dash_cooldown = max(0.5, base_cooldown - dexterity_reduction)  # Minimum 0.5s cooldown
            
            # Get current movement direction
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_d] - keys[pygame.K_a]
            dy = keys[pygame.K_s] - keys[pygame.K_w]
            
            # If no direction is pressed, dash in the last movement direction
            if dx == 0 and dy == 0:
                if self.direction.x != 0 or self.direction.y != 0:
                    dx = self.direction.x
                    dy = self.direction.y
                else:
                    return  # Can't dash if no direction
            
            # Normalize direction
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length
            
            # Store dash properties
            self.dash_active = True
            self.dash_direction = pygame.math.Vector2(dx, dy)
            self.dash_duration = 0.2  # Reduced from 0.3 to 0.2 seconds
            self.dash_speed = self.speed * 1.5  # Reduced from 2x to 1.5x speed
            
            # Add initial poof
            self.dash_poofs.append({
                'x': self.x,
                'y': self.y,
                'duration': 0.2,
                'opacity': 255
            }) 