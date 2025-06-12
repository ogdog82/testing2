class BaseState:
    def __init__(self, game):
        self.game = game
        
    def handle_event(self, event):
        """Handle pygame events"""
        pass
        
    def update(self, dt):
        """Update game logic"""
        pass
        
    def render(self, screen):
        """Render the state to the screen"""
        pass
        
    def enter(self):
        """Called when entering this state"""
        pass
        
    def exit(self):
        """Called when exiting this state"""
        pass 