# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
TITLE = "2D Roguelike RPG"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# Player settings
PLAYER_SPEED = 7  # Increased from 5
PLAYER_HEALTH = 100
PLAYER_MANA = 100
PLAYER_ATTACK_RANGE = 100
PLAYER_ATTACK_SPEED = 1.0  # Attacks per second
PLAYER_KNOCKBACK_FORCE = 10  # Force of knockback
PLAYER_KNOCKBACK_DURATION = 0.2  # Duration of knockback in seconds

# Combat settings
AUTO_ATTACK_DAMAGE = 10
SKILL_COOLDOWN_REDUCTION = 0.1  # 10% cooldown reduction per level

# Dungeon settings
ROOM_MIN_SIZE = 15
ROOM_MAX_SIZE = 30
MIN_ROOMS = 20
MAX_ROOMS = 30
CORRIDOR_WIDTH = 3
DUNGEON_WIDTH = 100  # Grid cells
DUNGEON_HEIGHT = 100  # Grid cells

# UI settings
UI_PADDING = 10
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
MANA_BAR_WIDTH = 200
MANA_BAR_HEIGHT = 20
SKILL_ICON_SIZE = 50

# Enemy settings
ENEMY_SPEED = 5.6  # Increased from 4 (maintaining the same ratio with player speed)
ENEMY_HEALTH = 100
ENEMY_DAMAGE = 10
ENEMY_ATTACK_RANGE = 50
ENEMY_ATTACK_SPEED = 1.0
ENEMY_DETECTION_RANGE = 300  # Pixels

# Item settings
ITEM_RARITY_CHANCES = {
    'common': 60,
    'uncommon': 25,
    'rare': 10,
    'legendary': 5
}

# Experience settings
XP_PER_LEVEL = 100
XP_MULTIPLIER = 1.5  # XP required increases by 50% each level 