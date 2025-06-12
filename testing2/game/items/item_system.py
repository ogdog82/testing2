import random
from ..constants import ITEM_RARITY_CHANCES

class ItemSystem:
    def __init__(self):
        self.item_templates = {
            'weapon': {
                'sword': {
                    'name': 'Sword',
                    'base_damage': 10,
                    'base_speed': 1.0,
                    'rarity_modifiers': {
                        'common': {'damage': 1.0, 'speed': 1.0},
                        'uncommon': {'damage': 1.2, 'speed': 1.1},
                        'rare': {'damage': 1.5, 'speed': 1.2},
                        'legendary': {'damage': 2.0, 'speed': 1.3}
                    }
                },
                'staff': {
                    'name': 'Staff',
                    'base_damage': 8,
                    'base_speed': 1.2,
                    'base_mana': 20,
                    'rarity_modifiers': {
                        'common': {'damage': 1.0, 'speed': 1.0, 'mana': 1.0},
                        'uncommon': {'damage': 1.1, 'speed': 1.1, 'mana': 1.2},
                        'rare': {'damage': 1.3, 'speed': 1.2, 'mana': 1.5},
                        'legendary': {'damage': 1.5, 'speed': 1.3, 'mana': 2.0}
                    }
                }
            },
            'armor': {
                'leather': {
                    'name': 'Leather Armor',
                    'base_defense': 5,
                    'base_speed': 1.0,
                    'rarity_modifiers': {
                        'common': {'defense': 1.0, 'speed': 1.0},
                        'uncommon': {'defense': 1.2, 'speed': 1.1},
                        'rare': {'defense': 1.5, 'speed': 1.2},
                        'legendary': {'defense': 2.0, 'speed': 1.3}
                    }
                },
                'plate': {
                    'name': 'Plate Armor',
                    'base_defense': 10,
                    'base_speed': 0.8,
                    'rarity_modifiers': {
                        'common': {'defense': 1.0, 'speed': 1.0},
                        'uncommon': {'defense': 1.3, 'speed': 1.1},
                        'rare': {'defense': 1.6, 'speed': 1.2},
                        'legendary': {'defense': 2.0, 'speed': 1.3}
                    }
                }
            },
            'accessory': {
                'ring': {
                    'name': 'Ring',
                    'base_mana': 10,
                    'base_health': 10,
                    'rarity_modifiers': {
                        'common': {'mana': 1.0, 'health': 1.0},
                        'uncommon': {'mana': 1.2, 'health': 1.2},
                        'rare': {'mana': 1.5, 'health': 1.5},
                        'legendary': {'mana': 2.0, 'health': 2.0}
                    }
                },
                'amulet': {
                    'name': 'Amulet',
                    'base_mana': 15,
                    'base_health': 15,
                    'rarity_modifiers': {
                        'common': {'mana': 1.0, 'health': 1.0},
                        'uncommon': {'mana': 1.3, 'health': 1.3},
                        'rare': {'mana': 1.6, 'health': 1.6},
                        'legendary': {'mana': 2.0, 'health': 2.0}
                    }
                }
            },
            'consumable': {
                'health_potion': {
                    'name': 'Health Potion',
                    'base_heal': 30,
                    'rarity_modifiers': {
                        'common': {'heal': 1.0},
                        'uncommon': {'heal': 1.5},
                        'rare': {'heal': 2.0},
                        'legendary': {'heal': 3.0}
                    }
                },
                'mana_potion': {
                    'name': 'Mana Potion',
                    'base_mana': 30,
                    'rarity_modifiers': {
                        'common': {'mana': 1.0},
                        'uncommon': {'mana': 1.5},
                        'rare': {'mana': 2.0},
                        'legendary': {'mana': 3.0}
                    }
                }
            }
        }
        
    def generate_item(self, item_type=None, rarity=None):
        # If no item type specified, choose random
        if not item_type:
            item_type = random.choice(['weapon', 'armor', 'accessory', 'consumable'])
            
        # If no rarity specified, choose based on chances
        if not rarity:
            rarity_roll = random.randint(1, 100)
            cumulative = 0
            for r, chance in ITEM_RARITY_CHANCES.items():
                cumulative += chance
                if rarity_roll <= cumulative:
                    rarity = r
                    break
                    
        # Generate item based on type and rarity
        if item_type == 'consumable':
            # Generate consumable item
            consumable_types = ['health_potion', 'mana_potion']
            consumable_type = random.choice(consumable_types)
            
            if consumable_type == 'health_potion':
                heal_amount = {
                    'common': 20,
                    'uncommon': 40,
                    'rare': 60,
                    'legendary': 100
                }[rarity]
                return {
                    'name': f"{rarity.capitalize()} Health Potion",
                    'type': 'consumable',
                    'heal': heal_amount,
                    'rarity': rarity
                }
            else:  # mana_potion
                mana_amount = {
                    'common': 15,
                    'uncommon': 30,
                    'rare': 45,
                    'legendary': 75
                }[rarity]
                return {
                    'name': f"{rarity.capitalize()} Mana Potion",
                    'type': 'consumable',
                    'mana': mana_amount,
                    'rarity': rarity
                }
        else:
            # Generate equipment item
            item = {
                'name': f"{rarity.capitalize()} {item_type.capitalize()}",
                'type': item_type,
                'rarity': rarity
            }
            
            # Add stats based on type and rarity
            if item_type == 'weapon':
                item['damage'] = {
                    'common': 5,
                    'uncommon': 10,
                    'rare': 15,
                    'legendary': 25
                }[rarity]
            elif item_type == 'armor':
                item['defense'] = {
                    'common': 3,
                    'uncommon': 6,
                    'rare': 9,
                    'legendary': 15
                }[rarity]
            elif item_type == 'accessory':
                # Random stat boost
                stat = random.choice(['strength', 'dexterity', 'intelligence', 'vitality'])
                item[stat] = {
                    'common': 2,
                    'uncommon': 4,
                    'rare': 6,
                    'legendary': 10
                }[rarity]
                
            return item
        
    def get_item_description(self, item):
        description = f"{item['name']}\n"
        description += f"Rarity: {item['rarity'].capitalize()}\n"
        
        # Add stats
        for stat, value in item.items():
            if stat not in ['type', 'name', 'rarity', 'template']:
                description += f"{stat.capitalize()}: {int(value)}\n"
                
        return description
        
    def get_item_value(self, item):
        # Base value based on rarity
        rarity_values = {
            'common': 10,
            'uncommon': 25,
            'rare': 100,
            'legendary': 500
        }
        
        base_value = rarity_values[item['rarity']]
        
        # Add value based on stats
        stat_value = 0
        for stat, value in item.items():
            if stat not in ['type', 'name', 'rarity', 'template']:
                stat_value += value
                
        return int(base_value + stat_value) 