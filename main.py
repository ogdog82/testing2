import pygame
import sys
from game.states.game_state import GameState
from game.states.menu_state import MenuState
from game.states.game_over_state import GameOverState
from game.states.shop_state import ShopState
from game.states.inventory_state import InventoryState
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE
from game.entities.player import Player
from game.dungeon.dungeon_generator import DungeonGenerator

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize player
        self.dungeon_generator = DungeonGenerator(100, 100)  # Default size
        self.dungeon_grid = self.dungeon_generator.generate()
        spawn_x, spawn_y = self.dungeon_generator.get_spawn_point()
        self.player = Player(spawn_x * 32, spawn_y * 32)  # 32 is tile_size
        
        # Initialize game states
        self.states = {
            'menu': MenuState(self),
            'game': GameState(self),
            'game_over': GameOverState(self),
            'shop': ShopState(self),
            'inventory': InventoryState(self)
        }
        self.current_state = self.states['menu']  # Store the actual state object
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i and self.current_state == self.states['game']:
                    self.change_state('inventory')
            self.current_state.handle_event(event)
            
    def update(self):
        dt = self.clock.get_time() / 1000.0  # Convert milliseconds to seconds
        self.current_state.update(dt)
        
    def render(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        self.current_state.render(self.screen)
        pygame.display.flip()
        
    def change_state(self, state_name):
        if state_name in self.states:
            self.current_state = self.states[state_name]
            
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 