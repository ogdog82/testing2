# 2D Roguelike RPG Game

A Python-based 2D roguelike RPG game featuring dungeon exploration, combat, inventory management, and a shop system.

## Features

- Procedurally generated dungeons
- Turn-based combat system
- Inventory management
- Shop system for buying and selling items
- Multiple game states (inventory, game over, etc.)
- Enemy AI and combat mechanics

## Requirements

- Python 3.9 or higher
- Required packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Project Structure

- `game/` - Main game package
  - `constants.py` - Game constants and configuration
  - `dungeon/` - Dungeon generation and management
  - `entities/` - Player, enemies, and other game entities
  - `items/` - Item system and item definitions
  - `shop/` - Shop system implementation
  - `states/` - Game states (inventory, game over, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license] 