#!/usr/bin/env python3
"""
Rubik's Cube Visualizer

This script visualizes a Rubik's Cube in 3D using PyGame and OpenGL.
It can display the cube state and animate moves.
"""

import sys
import os
import math
import time
import pygame as pg
from pygame.locals import *

# First, check if PyOpenGL is installed
try:
    # Try to import OpenGL modules
    from OpenGL import GL, GLU
    print("PyOpenGL is installed and imported successfully.")
except ImportError:
    # If import fails, try to install PyOpenGL
    print("PyOpenGL not found. Attempting to install...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyOpenGL", "PyOpenGL_accelerate"])
        print("PyOpenGL installed successfully. Importing...")
        from OpenGL import GL, GLU
    except Exception as e:
        print(f"Error installing or importing PyOpenGL: {e}")
        print("Please manually install PyOpenGL with: pip install PyOpenGL PyOpenGL_accelerate")
        sys.exit(1)

# Check for NumPy
try:
    import numpy as np
    print("NumPy is installed and imported successfully.")
except ImportError:
    print("NumPy not found. Attempting to install...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
        import numpy as np
    except Exception as e:
        print(f"Error installing or importing NumPy: {e}")
        print("Please manually install NumPy with: pip install numpy")
        sys.exit(1)

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Color definitions (RGB)
COLORS = {
    'U': (1.0, 1.0, 1.0),  # White (Up)
    'R': (1.0, 0.0, 0.0),  # Red (Right)
    'F': (0.0, 1.0, 0.0),  # Green (Front)
    'D': (1.0, 1.0, 0.0),  # Yellow (Down)
    'L': (1.0, 0.5, 0.0),  # Orange (Left)
    'B': (0.0, 0.0, 1.0),  # Blue (Back)
    'X': (0.2, 0.2, 0.2),  # Gray (for background/placeholder)
}

# Cube face definitions
FACES = {
    'U': [(x, 1.0, z) for z in [-1, 0, 1] for x in [-1, 0, 1]],  # Up face
    'D': [(x, -1.0, z) for z in [1, 0, -1] for x in [-1, 0, 1]],  # Down face
    'F': [(x, y, 1.0) for y in [-1, 0, 1] for x in [-1, 0, 1]],  # Front face
    'B': [(x, y, -1.0) for y in [-1, 0, 1] for x in [1, 0, -1]],  # Back face
    'L': [(-1.0, y, z) for z in [1, 0, -1] for y in [-1, 0, 1]],  # Left face
    'R': [(1.0, y, z) for z in [-1, 0, 1] for y in [-1, 0, 1]],   # Right face
}

# Face normals for lighting
FACE_NORMALS = {
    'U': (0, 1, 0),
    'D': (0, -1, 0),
    'F': (0, 0, 1),
    'B': (0, 0, -1),
    'L': (-1, 0, 0),
    'R': (1, 0, 0),
}

# Move definitions
MOVES = {
    'U': ('U', 1),  # Up clockwise
    "U'": ('U', -1),  # Up counter-clockwise
    'U2': ('U', 2),  # Up 180 degrees
    'D': ('D', 1),
    "D'": ('D', -1),
    'D2': ('D', 2),
    'F': ('F', 1),
    "F'": ('F', -1),
    'F2': ('F', 2),
    'B': ('B', 1),
    "B'": ('B', -1),
    'B2': ('B', 2),
    'L': ('L', 1),
    "L'": ('L', -1),
    'L2': ('L', 2),
    'R': ('R', 1),
    "R'": ('R', -1),
    'R2': ('R', 2),
}

# Rotation axes for each face
ROTATION_AXES = {
    'U': (0, 1, 0),  # Y-axis
    'D': (0, 1, 0),
    'F': (0, 0, 1),  # Z-axis
    'B': (0, 0, 1),
    'L': (1, 0, 0),  # X-axis
    'R': (1, 0, 0),
}


class CubeVisualizer:
    def __init__(self, cube_string=None):
        """
        Initialize the cube visualizer.
        
        Parameters:
        -----------
        cube_string : str, optional
            54-character string representing the cube state.
            If None, a solved cube is created.
        """
        # Initialize PyGame
        pg.init()
        self.display_size = (800, 600)
        self.display = pg.display.set_mode(
            self.display_size, 
            pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE
        )
        pg.display.set_caption("Rubik's Cube Visualizer")
        
        # Set up the clock
        self.clock = pg.time.Clock()
        
        # Initialize OpenGL
        self.init_gl()
        
        # Set up the cube state
        self.cube_string = cube_string if cube_string else "U" * 9 + "R" * 9 + "F" * 9 + "D" * 9 + "L" * 9 + "B" * 9
        
        # Animation state
        self.animating = False
        self.animation_start_time = 0
        self.animation_duration = 0.5  # seconds
        self.current_move = None
        self.move_queue = []
        
        # Camera rotation
        self.rotation_x = 30
        self.rotation_y = -45
        self.distance = 10
        
        # Mouse state for rotation
        self.dragging = False
        self.last_mouse_pos = None

    def init_gl(self):
        """Initialize OpenGL settings."""
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glColorMaterial(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE)
        
        # Set up light
        GL.glLight(GL.GL_LIGHT0, GL.GL_POSITION, (5, 5, 10, 1))
        GL.glLight(GL.GL_LIGHT0, GL.GL_DIFFUSE, (1, 1, 1, 1))
        
        # Set up perspective
        self.resize_display(*self.display_size)

    def resize_display(self, width, height):
        """Resize the display and update the perspective."""
        if height == 0:
            height = 1
        
        self.display_size = (width, height)
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        aspect_ratio = width / height
        GLU.gluPerspective(45, aspect_ratio, 0.1, 100.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def set_cube_state(self, cube_string):
        """Set the cube state from a 54-character string."""
        if len(cube_string) != 54:
            raise ValueError("Cube string must be 54 characters long")
        self.cube_string = cube_string

    def queue_moves(self, moves):
        """Queue a sequence of moves to be animated."""
        if isinstance(moves, str):
            moves = moves.split()
        self.move_queue.extend(moves)

    def apply_move(self, move):
        """
        Apply a move to the cube state.
        
        This is a simplified implementation that doesn't actually update the cube state.
        In a real implementation, this would update the cube_string based on the move.
        """
        # This is where you would update the cube_string based on the move
        # For now, we'll just print the move
        print(f"Applying move: {move}")
        
        # In a real implementation, you would update the cube_string here
        # based on the move and the current state

    def draw_cube(self):
        """Draw the Rubik's Cube with the current state."""
        # Clear the screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        # Set up the camera
        GL.glLoadIdentity()
        GL.glTranslatef(0, 0, -self.distance)
        GL.glRotatef(self.rotation_x, 1, 0, 0)
        GL.glRotatef(self.rotation_y, 0, 1, 0)
        
        # Draw each face of the cube
        for face, positions in FACES.items():
            face_index = "URFDLB".index(face)
            
            for i, pos in enumerate(positions):
                # Get the color for this position
                color_index = face_index * 9 + i
                color_char = self.cube_string[color_index]
                color = COLORS[color_char]
                
                # Draw the sticker
                self.draw_sticker(pos, color, FACE_NORMALS[face])
        
        # Update the display
        pg.display.flip()

    def draw_sticker(self, position, color, normal):
        """Draw a single sticker on the cube."""
        x, y, z = position
        
        # Scale to make gaps between stickers
        scale = 0.9
        
        # Calculate the four corners of the sticker
        if abs(normal[0]) == 1:  # X-axis normal (L/R faces)
            corners = [
                (x, y - scale/2, z - scale/2),
                (x, y + scale/2, z - scale/2),
                (x, y + scale/2, z + scale/2),
                (x, y - scale/2, z + scale/2)
            ]
        elif abs(normal[1]) == 1:  # Y-axis normal (U/D faces)
            corners = [
                (x - scale/2, y, z - scale/2),
                (x + scale/2, y, z - scale/2),
                (x + scale/2, y, z + scale/2),
                (x - scale/2, y, z + scale/2)
            ]
        else:  # Z-axis normal (F/B faces)
            corners = [
                (x - scale/2, y - scale/2, z),
                (x + scale/2, y - scale/2, z),
                (x + scale/2, y + scale/2, z),
                (x - scale/2, y + scale/2, z)
            ]
        
        # Draw the sticker
        GL.glColor3f(*color)
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(*normal)
        for corner in corners:
            GL.glVertex3f(*corner)
        GL.glEnd()

    def handle_events(self):
        """Handle PyGame events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return False
                
                # Handle key presses for moves
                key_to_move = {
                    pg.K_u: 'U',
                    pg.K_d: 'D',
                    pg.K_f: 'F',
                    pg.K_b: 'B',
                    pg.K_l: 'L',
                    pg.K_r: 'R',
                }
                
                if event.key in key_to_move:
                    move = key_to_move[event.key]
                    if pg.key.get_mods() & pg.KMOD_SHIFT:
                        move += "'"
                    self.queue_moves([move])
            
            elif event.type == pg.VIDEORESIZE:
                self.resize_display(event.w, event.h)
            
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.dragging = True
                    self.last_mouse_pos = event.pos
            
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.dragging = False
            
            elif event.type == pg.MOUSEMOTION:
                if self.dragging and self.last_mouse_pos:
                    dx, dy = event.pos[0] - self.last_mouse_pos[0], event.pos[1] - self.last_mouse_pos[1]
                    self.rotation_y += dx * 0.5
                    self.rotation_x += dy * 0.5
                    self.last_mouse_pos = event.pos
        
        return True

    def update(self):
        """Update the cube state and animations."""
        current_time = time.time()
        
        # If we're not currently animating and there are moves in the queue
        if not self.animating and self.move_queue:
            # Start animating the next move
            self.current_move = self.move_queue.pop(0)
            self.animating = True
            self.animation_start_time = current_time
        
        # If we're animating
        if self.animating:
            # Calculate animation progress
            progress = (current_time - self.animation_start_time) / self.animation_duration
            
            # If the animation is complete
            if progress >= 1.0:
                # Apply the move to the cube state
                self.apply_move(self.current_move)
                self.animating = False
                self.current_move = None

    def run(self):
        """Main loop for the visualizer."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw_cube()
            self.clock.tick(60)
        
        pg.quit()


def main():
    """Main function to run the visualizer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rubik's Cube Visualizer")
    parser.add_argument("--cube", help="54-character string representing the cube state")
    parser.add_argument("--moves", help="Space-separated list of moves to apply")
    
    args = parser.parse_args()
    
    visualizer = CubeVisualizer(args.cube)
    
    if args.moves:
        visualizer.queue_moves(args.moves)
    
    visualizer.run()


if __name__ == "__main__":
    main()



