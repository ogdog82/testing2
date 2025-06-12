import random
from ..items.item_system import ItemSystem

class ShopSystem:
    def __init__(self):
        self.item_system = ItemSystem()
        self.inventory = []
        self.refresh_shop()
        
    def refresh_shop(self):
        # Clear current inventory
        self.inventory = []
        
        # Generate new items
        num_items = random.randint(3, 6)
        for _ in range(num_items):
            item = self.item_system.generate_item()
            self.inventory.append(item)
            
    def get_shop_inventory(self):
        return self.inventory
        
    def buy_item(self, player, item_index):
        if item_index < 0 or item_index >= len(self.inventory):
            return False, "Invalid item selection"
            
        item = self.inventory[item_index]
        price = self.item_system.get_item_value(item)
        
        # Check if player has enough gold
        if not player.inventory.remove_gold(price):
            return False, "Not enough gold"
            
        # Check if player has inventory space
        if not player.inventory.add_item(item):
            player.inventory.add_gold(price)  # Refund the gold
            return False, "Inventory full"
            
        # Remove item from shop
        self.inventory.pop(item_index)
        return True, f"Bought {item['name']} for {price} gold"
        
    def sell_item(self, player, item_index):
        if item_index < 0 or item_index >= len(player.inventory.items):
            return False, "Invalid item selection"
            
        item = player.inventory.items[item_index]
        price = self.item_system.get_item_value(item) // 2  # Sell for half value
        
        # Add gold to player
        player.inventory.add_gold(price)
        
        # Remove item from player inventory
        player.inventory.remove_item(item)
        return True, f"Sold {item['name']} for {price} gold"
        
    def get_shop_description(self):
        description = "Shop Inventory:\n"
        for i, item in enumerate(self.inventory):
            price = self.item_system.get_item_value(item)
            description += f"{i + 1}. {item['name']} - {price} gold\n"
            description += self.item_system.get_item_description(item)
            description += "\n"
        return description 