import random
import noise
import numpy as np
import pygame
from ..constants import (
    ROOM_MIN_SIZE, ROOM_MAX_SIZE,
    MIN_ROOMS, MAX_ROOMS,
    CORRIDOR_WIDTH
)

class Room:
    def __init__(self, x, y, width, height, room_type='combat'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.connected = False
        self.room_type = room_type  # 'entrance', 'exit', 'shop', 'combat'
        self.connections = []  # List of connected rooms
        self.stairs = []  # List of stair positions for entrance/exit rooms
        
    def center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)
        
    def intersects(self, other, padding=0):
        return self.rect.inflate(padding, padding).colliderect(other.rect)
        
    def add_stairs(self, direction='up'):
        """Add stairs to the room. Direction can be 'up' for entrance or 'down' for exit."""
        # Clear existing stairs
        self.stairs = []
        
        # Calculate stair position (center of room)
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Add a single stair position
        self.stairs.append((center_x, center_y, direction))

class DungeonGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rooms = []
        self.corridors = []
        self.grid = np.zeros((height, width), dtype=int)
        self.entrance_room = None
        self.exit_room = None
        self.shop_rooms = []
        self.boss_room = None
        self.current_dungeon_level = 1
        
    def generate(self, dungeon_level=1):
        self.current_dungeon_level = dungeon_level
        # Maximum number of attempts to generate a valid dungeon
        max_attempts = 10
        attempts = 0
        
        while attempts < max_attempts:
            # Clear previous generation
            self.rooms = []
            self.corridors = []
            self.grid.fill(0)
            self.entrance_room = None
            self.exit_room = None
            self.shop_rooms = []
            self.boss_room = None
            
            # Generate rooms with purpose
            num_rooms = max(4, random.randint(30, 40))  # Ensure minimum of 4 rooms
            
            # First, create entrance room at the left side
            entrance_x = 5
            entrance_y = random.randint(5, self.height - ROOM_MAX_SIZE - 5)
            entrance_width = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            entrance_height = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            self.entrance_room = Room(entrance_x, entrance_y, entrance_width, entrance_height, 'entrance')
            self.entrance_room.add_stairs('up')  # Add upward stairs
            self.rooms.append(self.entrance_room)
            self.grid[entrance_y:entrance_y+entrance_height, entrance_x:entrance_x+entrance_width] = 1
            
            # Calculate room spacing and grid
            room_spacing = 10
            grid_width = 5  # Number of columns in the room grid
            grid_height = (num_rooms - 2) // grid_width + 1  # -2 for entrance and exit
            
            # Generate combat rooms and shops in a grid pattern
            current_x = entrance_x + entrance_width + room_spacing
            current_y = 5
            room_count = 0
            
            # Add shop room every 3rd dungeon
            should_add_shop = (dungeon_level % 3 == 0)
            
            # Add boss room every 5th dungeon
            should_add_boss = (dungeon_level % 5 == 0)
            
            # Track if we've added special rooms
            shop_added = False
            boss_added = False
            
            for row in range(grid_height):
                for col in range(grid_width):
                    if room_count >= num_rooms - 2:  # -2 for entrance and exit
                        break
                        
                    # Determine room type based on position and count
                    room_type = 'combat'
                    
                    # Add shop room if this is a shop dungeon and we haven't added one yet
                    if should_add_shop and not shop_added and room_count == num_rooms // 3:
                        room_type = 'shop'
                        shop_added = True
                    
                    # Add boss room if this is a boss dungeon and we haven't added one yet
                    if should_add_boss and not boss_added and room_count == num_rooms // 2:
                        room_type = 'boss'
                        boss_added = True
                    
                    # Calculate room position
                    room_x = current_x + (col * (ROOM_MAX_SIZE + room_spacing))
                    room_y = current_y + (row * (ROOM_MAX_SIZE + room_spacing))
                    
                    # Ensure room stays within bounds
                    if room_x + ROOM_MAX_SIZE >= self.width - ROOM_MAX_SIZE:
                        break
                        
                    # Generate room with random size
                    room_width = random.randint(ROOM_MIN_SIZE, min(ROOM_MAX_SIZE, 20))
                    room_height = random.randint(ROOM_MIN_SIZE, min(ROOM_MAX_SIZE, 20))
                    
                    new_room = Room(room_x, room_y, room_width, room_height, room_type)
                    self.rooms.append(new_room)
                    self.grid[room_y:room_y+room_height, room_x:room_x+room_width] = 1
                    
                    if room_type == 'shop':
                        self.shop_rooms.append(new_room)
                    elif room_type == 'boss':
                        self.boss_room = new_room
                        
                    room_count += 1
                    
            # Create exit room at the right side
            exit_x = self.width - ROOM_MAX_SIZE - 5
            exit_y = random.randint(5, self.height - ROOM_MAX_SIZE - 5)
            exit_width = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            exit_height = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            
            # On every 5th dungeon, make the exit room a boss room
            if dungeon_level % 5 == 0:
                self.exit_room = Room(exit_x, exit_y, exit_width, exit_height, 'boss')
                self.boss_room = self.exit_room  # Set boss room to be the exit room
            else:
                self.exit_room = Room(exit_x, exit_y, exit_width, exit_height, 'exit')
                
            self.exit_room.add_stairs('down')  # Add downward stairs
            self.rooms.append(self.exit_room)
            self.grid[exit_y:exit_y+exit_height, exit_x:exit_x+exit_width] = 1
            
            # If this is a shop dungeon and we haven't added a shop yet, add it to the exit room
            if should_add_shop and not shop_added:
                shop_room = Room(exit_x, exit_y, exit_width, exit_height, 'shop')
                self.shop_rooms.append(shop_room)
                shop_added = True
            
            # Connect rooms in a more structured way
            self._connect_rooms_structured()
            
            # Add walls
            self._add_walls()
            
            # Ensure dungeon is completely enclosed
            self._enforce_boundaries()
            
            # Verify that all rooms are connected and exit is accessible
            if self._verify_all_rooms_connected() and self._verify_exit_connection():
                return self.grid
                
            attempts += 1
            
        # If we've exhausted all attempts, create a simple guaranteed valid dungeon
        return self._create_fallback_dungeon()
        
    def _create_fallback_dungeon(self):
        """Create a simple, guaranteed valid dungeon with a clear path to exit."""
        # Clear everything
        self.rooms = []
        self.corridors = []
        self.grid.fill(0)
        
        # Create a simple entrance room
        entrance_x = 5
        entrance_y = self.height // 2 - 10
        entrance_width = 15
        entrance_height = 15
        self.entrance_room = Room(entrance_x, entrance_y, entrance_width, entrance_height, 'entrance')
        self.entrance_room.add_stairs('up')
        self.rooms.append(self.entrance_room)
        self.grid[entrance_y:entrance_y+entrance_height, entrance_x:entrance_x+entrance_width] = 1
        
        # Create a simple exit room
        exit_x = self.width - 20
        exit_y = self.height // 2 - 10
        exit_width = 15
        exit_height = 15
        self.exit_room = Room(exit_x, exit_y, exit_width, exit_height, 'exit')
        self.exit_room.add_stairs('down')
        self.rooms.append(self.exit_room)
        self.grid[exit_y:exit_y+exit_height, exit_x:exit_x+exit_width] = 1
        
        # Create a direct corridor between entrance and exit
        corridor_y = self.height // 2
        for x in range(entrance_x + entrance_width, exit_x):
            for y in range(corridor_y - 2, corridor_y + 3):  # 5 tiles wide corridor
                self.grid[y, x] = 1
                
        # Add walls
        self._add_walls()
        self._enforce_boundaries()
        
        # Connect the rooms
        self.entrance_room.connections.append(self.exit_room)
        self.exit_room.connections.append(self.entrance_room)
        
        return self.grid
        
    def _connect_rooms_structured(self):
        # Sort rooms by x coordinate for basic progression
        sorted_rooms = sorted(self.rooms, key=lambda r: r.center()[0])
        
        # First, ensure all rooms are connected in sequence
        for i in range(len(sorted_rooms) - 1):
            room1 = sorted_rooms[i]
            room2 = sorted_rooms[i + 1]
            
            # Get room centers
            x1, y1 = room1.center()
            x2, y2 = room2.center()
            
            # Create L-shaped corridor
            if random.random() < 0.5:
                # Horizontal then vertical
                self._create_corridor(x1, y1, x2, y1)
                self._create_corridor(x2, y1, x2, y2)
            else:
                # Vertical then horizontal
                self._create_corridor(x1, y1, x1, y2)
                self._create_corridor(x1, y2, x2, y2)
                
            # Add connection to room objects
            room1.connections.append(room2)
            room2.connections.append(room1)
            
        # Then, add additional connections to ensure all rooms are reachable
        for room in sorted_rooms:
            # Find the closest unconnected room
            unconnected = [r for r in sorted_rooms if r not in room.connections and r != room]
            if unconnected:
                closest = min(unconnected, key=lambda r: self._distance_between_rooms(room, r))
                x1, y1 = room.center()
                x2, y2 = closest.center()
                
                # Create L-shaped corridor
                if random.random() < 0.5:
                    self._create_corridor(x1, y1, x2, y1)
                    self._create_corridor(x2, y1, x2, y2)
                else:
                    self._create_corridor(x1, y1, x1, y2)
                    self._create_corridor(x1, y2, x2, y2)
                    
                # Add connection
                room.connections.append(closest)
                closest.connections.append(room)
                
    def _distance_between_rooms(self, room1, room2):
        """Calculate the Manhattan distance between two rooms."""
        x1, y1 = room1.center()
        x2, y2 = room2.center()
        return abs(x1 - x2) + abs(y1 - y2)
        
    def _verify_all_rooms_connected(self):
        """Verify that all rooms are connected to each other via corridors."""
        if not self.rooms:
            return False
            
        # Use BFS to check if all rooms are reachable from the entrance
        visited = set()
        queue = [self.entrance_room]
        
        while queue:
            current = queue.pop(0)
            visited.add(current)
            
            for connected in current.connections:
                if connected not in visited:
                    queue.append(connected)
                    
        # Check if all rooms were visited
        return len(visited) == len(self.rooms)
        
    def _create_corridor(self, x1, y1, x2, y2):
        # Create horizontal corridor (minimum 2 tiles wide)
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(y1 - 2, y1 + 3):  # 5 tiles wide corridor
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y, x] = 1
                    
        # Create vertical corridor (minimum 2 tiles wide)
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(x2 - 2, x2 + 3):  # 5 tiles wide corridor
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y, x] = 1
                    
    def _add_walls(self):
        # Create a copy of the grid
        new_grid = self.grid.copy()
        
        # Add walls only around floor tiles that are adjacent to empty space
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] == 1:  # Floor tile
                    # Check surrounding tiles
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < self.width and 0 <= ny < self.height and
                                self.grid[ny, nx] == 0):  # Empty space
                                new_grid[ny, nx] = 2  # Wall tile
                                
        self.grid = new_grid
        
    def get_spawn_point(self):
        # Use entrance room for player spawn
        if self.entrance_room:
            x, y = self.entrance_room.center()
            return (x, y)
            
        # Fallback to random floor tile
        floor_tiles = np.where(self.grid == 1)
        if len(floor_tiles[0]) > 0:
            idx = random.randint(0, len(floor_tiles[0]) - 1)
            return (floor_tiles[1][idx], floor_tiles[0][idx])
        return (self.width // 2, self.height // 2)
        
    def get_enemy_spawn_points(self, num_enemies):
        # Get all walkable floor tiles
        floor_tiles = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:  # Floor tile
                    # Skip tiles that are too close to entrance or exit
                    if self.entrance_room and self.entrance_room.rect.collidepoint(x, y):
                        continue
                    if self.exit_room and self.exit_room.rect.collidepoint(x, y):
                        continue
                    floor_tiles.append((x, y))
        
        # If no valid floor tiles, return empty list
        if not floor_tiles:
            return []
            
        # Randomly select spawn points from floor tiles
        spawn_points = []
        for _ in range(num_enemies):
            if floor_tiles:  # Check if we still have valid tiles
                spawn_point = random.choice(floor_tiles)
                spawn_points.append(spawn_point)
                # Remove the chosen tile to prevent multiple enemies spawning in the same spot
                floor_tiles.remove(spawn_point)
                
        return spawn_points
        
    def get_room_at_position(self, x, y):
        # Find which room contains the given position
        for room in self.rooms:
            if room.rect.collidepoint(x, y):
                return room
        return None 

    def _enforce_boundaries(self):
        # Add walls only around the perimeter of the dungeon
        for x in range(self.width):
            for y in range(self.height):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.grid[y, x] = 2  # Wall
                    
        # Check for any floor tiles adjacent to the edge
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y, x] == 1:  # Floor tile
                    # Check if it's adjacent to the edge
                    if (x == 1 or x == self.width - 2 or 
                        y == 1 or y == self.height - 2):
                        # Add walls around this floor tile
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                if (0 <= y + dy < self.height and 
                                    0 <= x + dx < self.width and 
                                    self.grid[y + dy, x + dx] == 0):  # Empty space
                                    self.grid[y + dy, x + dx] = 2  # Wall 

    def _verify_exit_connection(self):
        """Verify that the exit room is properly placed and connected."""
        if not self.exit_room or not self.entrance_room:
            return False
            
        # Check if exit room has any connections
        if not self.exit_room.connections:
            return False
            
        # Check if exit room is properly placed (not overlapping with other rooms)
        for room in self.rooms:
            if room != self.exit_room and room.intersects(self.exit_room):
                return False
                
        # Check if there's a path from entrance to exit using BFS
        visited = set()
        queue = [(self.entrance_room, [self.entrance_room])]
        
        while queue:
            current_room, path = queue.pop(0)
            if current_room == self.exit_room:
                return True
                
            visited.add(current_room)
            for connected in current_room.connections:
                if connected not in visited:
                    queue.append((connected, path + [connected]))
                    
        return False

    def get_stair_positions(self):
        """Return the positions of all stairs in the dungeon."""
        stairs = []
        if self.entrance_room:
            stairs.extend(self.entrance_room.stairs)
        if self.exit_room:
            stairs.extend(self.exit_room.stairs)
        return stairs 

    def get_room_type_at_position(self, x, y):
        """Get the type of room at the given position."""
        for room in self.rooms:
            if room.rect.collidepoint(x, y):
                return room.room_type
        return None 

    def get_shop_position(self):
        """Get the position of the shop icon in the current dungeon."""
        if not self.shop_rooms:
            return None
            
        # Use the first shop room
        shop_room = self.shop_rooms[0]
        
        # Place the shop icon in the center of the room, offset from stairs
        shop_x = shop_room.x + shop_room.width // 2
        shop_y = shop_room.y + shop_room.height // 2
        
        # Offset the shop position to avoid stairs
        # If the room is wide enough, place it to the right of center
        if shop_room.width > 10:
            shop_x += 3
        # If the room is tall enough, place it below center
        if shop_room.height > 10:
            shop_y += 3
            
        return (shop_x, shop_y)

    def get_boss_room(self):
        """Get the boss room for the current dungeon level."""
        if self.current_dungeon_level % 5 == 0:
            for room in self.rooms:
                if room.room_type == 'boss':
                    return room
        return None 