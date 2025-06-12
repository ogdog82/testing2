class Inventory:
    def __init__(self, max_size=20):
        self.max_size = max_size
        self.items = []
        self.equipped = {
            'weapon': None,
            'armor': None,
            'accessory': None
        }
        self.gold = 0
        
    def add_item(self, item):
        if len(self.items) >= self.max_size:
            return False
        self.items.append(item)
        return True
        
    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False
        
    def equip_item(self, item):
        if item not in self.items:
            return False
            
        # Check if item type is valid
        if item['type'] not in self.equipped:
            return False
            
        # Unequip current item of same type if exists
        if self.equipped[item['type']]:
            self.unequip_item(item['type'])
            
        # Remove item from inventory and equip it
        self.items.remove(item)
        self.equipped[item['type']] = item
        return True
        
    def unequip_item(self, slot):
        if slot not in self.equipped:
            return False
            
        if self.equipped[slot]:
            if len(self.items) < self.max_size:
                self.items.append(self.equipped[slot])
                self.equipped[slot] = None
                return True
        return False
        
    def use_consumable(self, item):
        if item not in self.items or item.get('type') != 'consumable':
            return False
            
        # Apply consumable effects
        effects = {}
        for stat, value in item.items():
            if stat not in ['type', 'name', 'rarity', 'template']:
                effects[stat] = value
                
        # Remove consumed item
        self.items.remove(item)
        return effects
        
    def get_equipped_stats(self):
        stats = {
            'strength': 0,
            'dexterity': 0,
            'intelligence': 0,
            'vitality': 0,
            'damage': 0,
            'defense': 0,
            'speed': 1.0,
            'mana': 0,
            'health': 0,
            'attack_range': 0,
            'attack_speed': 0
        }
        
        # Sum up stats from equipped items
        for item in self.equipped.values():
            if item:
                for stat, value in item.items():
                    if stat in stats:
                        stats[stat] += value
                        
        return stats
        
    def add_gold(self, amount):
        self.gold += amount
        
    def remove_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
        
    def get_inventory_space(self):
        return self.max_size - len(self.items)
        
    def is_full(self):
        return len(self.items) >= self.max_size 