#!/usr/bin/env python3
"""
Rubik's Cube Visualizer
"""

import sys
import os
import math
import time
import pygame as pg
from pygame.locals import *
from OpenGL import GL, GLU
import numpy as np
from twophase.solve import SolutionManager
import time

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# colour definitions
COLORS = {
    'U': (1.0, 1.0, 1.0),  # White (Up)
    'R': (1.0, 0.0, 0.0),  # Red (Right)
    'F': (0.0, 1.0, 0.0),  # Green (Front)
    'D': (1.0, 1.0, 0.0),  # Yellow (Down)
    'L': (1.0, 0.5, 0.0),  # Orange (Left)
    'B': (0.0, 0.0, 1.0),  # Blue (Back)
    'X': (0.2, 0.2, 0.2),  # Gray (for background)
}

# face definitions
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

# Move Permutations
MOVE_PERMUTATIONS = {
    'U': [(0, 2), (2, 8), (8, 6), (6, 0),
          (1, 5), (5, 7), (7, 3), (3, 1),
          (18, 9), (19, 10), (20, 11),
          (9, 47), (10, 46), (11, 45),
          (47, 36), (46, 37), (45, 38),
          (36, 18), (37, 19), (38, 20)],
    "U'": [(2, 0), (8, 2), (6, 8), (0, 6),
           (5, 1), (7, 5), (3, 7), (1, 3),
           (9, 18), (10, 19), (11, 20),
           (47, 9), (46, 10), (45, 11),
           (36, 47), (37, 46), (38, 45),
           (18, 36), (19, 37), (20, 38)],
    'U2': [(0, 8), (8, 0), (2, 6), (6, 2),
           (1, 7), (7, 1), (3, 5), (5, 3),
           (18, 47), (19, 46), (20, 45),
           (9, 36), (10, 37), (11, 38),
           (47, 18), (46, 19), (45, 20),
           (36, 9), (37, 10), (38, 11)],
    'D': [(27, 29), (29, 35), (35, 33), (33, 27),
          (28, 32), (32, 34), (34, 30), (30, 28),
          (24, 44), (23, 41), (22, 38),
          (44, 35), (43, 34), (42, 33),
          (35, 15), (34, 14), (33, 13),
          (15, 24), (14, 23), (13, 22)],
    "D'": [(29, 27), (35, 29), (33, 35), (27, 33),
           (32, 28), (34, 32), (30, 34), (28, 30),
           (24, 15), (23, 14), (22, 13),
           (44, 24), (41, 23), (38, 22),
           (35, 44), (34, 43), (33, 42),
           (15, 35), (14, 34), (13, 33)],
    'D2': [(27, 35), (35, 27), (29, 33), (33, 29),
           (28, 34), (34, 28), (30, 32), (32, 30),
           (24, 35), (23, 34), (22, 33),
           (44, 15), (41, 14), (38, 13),
           (35, 24), (34, 23), (33, 22),
           (15, 44), (14, 41), (13, 38)],
    'F': [(18, 20), (20, 26), (26, 24), (24, 18),
          (19, 23), (23, 25), (25, 21), (21, 19),
          (6, 36), (7, 39), (8, 42),
          (11, 6), (14, 7), (17, 8),
          (44, 11), (43, 14), (42, 17),
          (36, 44), (39, 43), (42, 42)],
    "F'": [(20, 18), (26, 20), (24, 26), (18, 24),
           (23, 19), (25, 23), (21, 25), (19, 21),
           (6, 11), (7, 14), (8, 17),
           (11, 44), (14, 43), (17, 42),
           (44, 36), (43, 39), (42, 42),
           (36, 6), (39, 7), (42, 8)],
    'F2': [(18, 26), (26, 18), (20, 24), (24, 20),
           (19, 25), (25, 19), (21, 23), (23, 21),
           (6, 44), (7, 43), (8, 42),
           (11, 36), (14, 39), (17, 42),
           (44, 6), (43, 7), (42, 8),
           (36, 11), (39, 14), (42, 17)],
    'B': [(45, 47), (47, 53), (53, 51), (51, 45),
          (46, 50), (50, 52), (52, 48), (48, 46),
          (0, 38), (1, 41), (2, 44),
          (36, 2), (37, 1), (38, 0),
          (27, 36), (28, 37), (29, 38),
          (2, 27), (1, 28), (0, 29)],
    "B'": [(47, 45), (53, 47), (51, 53), (45, 51),
           (50, 46), (52, 50), (48, 52), (46, 48),
           (0, 29), (1, 28), (2, 27),
           (36, 0), (37, 1), (38, 2),
           (27, 2), (28, 1), (29, 0),
           (2, 36), (1, 37), (0, 38)],
    'B2': [(45, 53), (53, 45), (47, 51), (51, 47),
           (46, 52), (52, 46), (48, 50), (50, 48),
           (0, 27), (1, 28), (2, 29),
           (36, 2), (37, 1), (38, 0),
           (27, 0), (28, 1), (29, 2),
           (2, 36), (1, 37), (0, 38)],
    'L': [(36, 38), (38, 44), (44, 42), (42, 36),
          (37, 41), (41, 43), (43, 39), (39, 37),
          (0, 18), (3, 21), (6, 24),
          (18, 27), (21, 30), (24, 33),
          (27, 45), (30, 48), (33, 51),
          (45, 0), (48, 3), (51, 6)],
    "L'": [(38, 36), (44, 38), (42, 44), (36, 42),
           (41, 37), (43, 41), (39, 43), (37, 39),
           (0, 45), (3, 48), (6, 51),
           (18, 0), (21, 3), (24, 6),
           (27, 18), (30, 21), (33, 24),
           (45, 27), (48, 30), (51, 33)],
    'L2': [(36, 44), (44, 36), (38, 42), (42, 38),
           (37, 43), (43, 37), (39, 41), (41, 39),
           (0, 27), (3, 30), (6, 33),
           (18, 45), (21, 48), (24, 51),
           (27, 0), (30, 3), (33, 6),
           (45, 18), (48, 21), (51, 24)],
    'R': [(9, 11), (11, 17), (17, 15), (15, 9),
          (10, 14), (14, 16), (16, 12), (12, 10),
          (8, 51), (5, 48), (2, 45),
          (47, 8), (44, 5), (41, 2),
          (35, 47), (32, 44), (29, 41),
          (45, 35), (48, 32), (51, 29)],
    "R'": [(11, 9), (17, 11), (15, 17), (9, 15),
           (14, 10), (16, 14), (12, 16), (10, 12),
           (8, 47), (5, 44), (2, 41),
           (51, 8), (48, 5), (45, 2),
           (35, 51), (32, 48), (29, 45),
           (47, 35), (44, 32), (41, 29)],
    'R2': [(9, 17), (17, 9), (11, 15), (15, 11),
           (10, 16), (16, 10), (12, 14), (14, 12),
           (8, 35), (5, 32), (2, 29),
           (47, 8), (44, 5), (41, 2),
           (35, 51), (32, 48), (29, 45),
           (51, 47), (48, 44), (45, 41)]
}
class CubeVisualizer:
    def __init__(self, cube_string=None):
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
        self.animation_duration = 0.5  
        self.current_move = None
        self.move_queue = []
        
        # Camera rotation
        self.rotation_x = 30
        self.rotation_y = -45
        self.distance = 10
        
        # Mouse state for rotation
        self.dragging = False
        self.last_mouse_pos = None
        self.solution_info = {
            "solved": False,
            "solution": [],
            "move_count": 0,
            "solve_time": 0.0
        }
        self.move_index = 0
        self.move_timer = 0
        

    def init_gl(self):
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glColorMaterial(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE)
    
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, (5.0, 5.0, 10.0, 1.0))
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))

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
        GL.glLoadIdentity()

    def set_cube_state(self, cube_string):
        """Set the cube state from a 54-character string."""
        if len(cube_string) != 54:
            raise ValueError("Cube string must be 54 characters long")
        self.cube_string = cube_string

    def queue_moves(self, solution_str, move_count, solve_time):
        self.solution_info["solved"] = True
        self.solution_info["solution"] = solution_str.split()
        self.solution_info["move_count"] = move_count
        self.solution_info["solve_time"] = solve_time
        self.move_index = 0
        self.move_timer = time.time()
        self.move_queue = self.solution_info["solution"]
        self.animating = False
        self.current_move = None

    def apply_move(self, move):
        """
        Apply a move to the cube state using the two-phase solver's internal representation.
        """
        if move not in MOVES:
            print(f"Move {move} not recognized.")
            return
        
        try:
            from twophase.cubes.facecube import FaceCube
            from twophase.cubes.cubiecube import CubieCube
            fc = FaceCube(self.cube_string)
            cc = fc.to_cubiecube()
            face, direction = MOVES[move]
            face_idx = "URFDLB".index(face)
            if direction == 1:  # Clockwise
                cc.move(face_idx)
            elif direction == -1:  # Counter-clockwise
                for _ in range(3):
                    cc.move(face_idx)
            elif direction == 2:  # 180 degrees
                cc.move(face_idx)
                cc.move(face_idx)
            new_fc = cc.to_facecube()
            self.cube_string = new_fc.to_string()
            print(f"Applied move: {move}") 
        except Exception as e:
            print(f"Error applying move {move}: {e}")

    def verify_solution(self):
        """Verify if the cube is in a solved state using the two-phase solver's representation."""
        from twophase.cubes.facecube import FaceCube
        fc = FaceCube(self.cube_string)
        cc = fc.to_cubiecube()
        return cc.verify() == 0

    def draw_cube(self):
        """Draw the Rubik's Cube with the current state."""
        # Clear the screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glLoadIdentity()
        GL.glTranslatef(0, 0, -self.distance)
        GL.glRotatef(self.rotation_x, 1, 0, 0)
        GL.glRotatef(self.rotation_y, 0, 1, 0)
        
        for face, positions in FACES.items():
            face_index = "URFDLB".index(face)
            
            for i, pos in enumerate(positions):
                color_index = face_index * 9 + i
                color_char = self.cube_string[color_index]
                color = COLORS[color_char]
                self.draw_sticker(pos, color, FACE_NORMALS[face])
        pg.display.flip()

    def draw_sticker(self, position, color, normal):
        """Draw a single sticker on the cube with proper offset and scaling."""
        x, y, z = position

        scale = 0.9 
        offset = 0.5  

        x += normal[0] * offset
        y += normal[1] * offset
        z += normal[2] * offset
        if abs(normal[0]) == 1:  # Left or Right face (X-axis)
            corners = [
                (x, y - scale/2, z - scale/2),
                (x, y + scale/2, z - scale/2),
                (x, y + scale/2, z + scale/2),
                (x, y - scale/2, z + scale/2)
            ]
        elif abs(normal[1]) == 1:  # Up or Down face (Y-axis)
            corners = [
                (x - scale/2, y, z - scale/2),
                (x + scale/2, y, z - scale/2),
                (x + scale/2, y, z + scale/2),
                (x - scale/2, y, z + scale/2)
            ]
        else:  # Front or Back face (Z-axis)
            corners = [
                (x - scale/2, y - scale/2, z),
                (x + scale/2, y - scale/2, z),
                (x + scale/2, y + scale/2, z),
                (x - scale/2, y + scale/2, z)
            ]
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
        if not self.animating and self.move_queue:
            self.current_move = self.move_queue.pop(0)
            self.animating = True
            self.animation_start_time = current_time

        if self.animating:
            progress = (current_time - self.animation_start_time) / self.animation_duration
            if progress >= 1.0:
                self.apply_move(self.current_move)
                self.animating = False
                self.current_move = None
                if not self.move_queue:
                    print("Final cube string:", self.cube_string)
                    if self.verify_solution():
                        print("Cube is SOLVED!")
                    else:
                        print("Cube is NOT solved.")
                        for face_idx, face in enumerate("URFDLB"):
                            start_idx = face_idx * 9
                            face_colors = self.cube_string[start_idx:start_idx+9]
                            print(f"Face {face}: {face_colors}")
    
    def rotate_face_visual(self, face, angle_degrees):
        """
        Visually rotate a face of the cube by a given angle.
        """
        GL.glPushMatrix()  
        axis = ROTATION_AXES[face]
        normal = FACE_NORMALS[face]
        if face == 'U':
            GL.glTranslatef(0, 1.0, 0)
        elif face == 'D':
            GL.glTranslatef(0, -1.0, 0)
        elif face == 'F':
            GL.glTranslatef(0, 0, 1.0)
        elif face == 'B':
            GL.glTranslatef(0, 0, -1.0)
        elif face == 'L':
            GL.glTranslatef(-1.0, 0, 0)
        elif face == 'R':
            GL.glTranslatef(1.0, 0, 0)
        GL.glRotatef(angle_degrees, *axis)
        if face in ['U', 'D']:
            GL.glTranslatef(0, -1.0 if face == 'U' else 1.0, 0)
        elif face in ['F', 'B']:
            GL.glTranslatef(0, 0, -1.0 if face == 'F' else 1.0)
        elif face in ['L', 'R']:
            GL.glTranslatef(-1.0 if face == 'L' else 1.0, 0, 0)
        positions = FACES[face]
        face_index = "URFDLB".index(face)
        for i, pos in enumerate(positions):
            color_index = face_index * 9 + i
            color_char = self.cube_string[color_index]
            color = COLORS[color_char]
            self.draw_sticker(pos, color, FACE_NORMALS[face])
        GL.glPopMatrix()
    
    def run(self):
        """Main loop for the visualizer."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw_cube()
            self.clock.tick(60)
        
        pg.quit()
    
    def draw_text_overlay(self):
        font = pg.font.SysFont("Arial", 24)
        if self.solution_info["solved"]:
            move_text = f"Moves: {self.solution_info['move_count']}"
            time_text = f"Time: {self.solution_info['solve_time']:.2f} sec"
            move_surf = font.render(move_text, True, (255, 255, 255))
            time_surf = font.render(time_text, True, (255, 255, 255))
            self.display.blit(move_surf, (10, 10))
            self.display.blit(time_surf, (10, 40))



def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--cube", help="Cube state as 54-character string")
    args = parser.parse_args()
    if args.cube:
        if len(args.cube) != 54:
            print("Error: Cube string must be 54 characters long")
            sys.exit(1)
        visualizer = CubeVisualizer(args.cube)

        start_time = time.time()
        try:
            from twophase import solve
            solution_str = solve(args.cube, max_length=25, max_time=10)

            solve_time = time.time() - start_time

            if solution_str:
                move_count = len(solution_str.split())
                print(f"[*] Solution: {solution_str}")
                print(f"[*] Moves: {move_count}")
                print(f"[*] Time: {solve_time:.2f}s")
                
                visualizer.queue_moves(solution_str, move_count, solve_time)
            else:
                print("[!] No solution found.")

        except ValueError as e:
            if "two corners or edges should be exchanged" in str(e):
                print("[!] Cube parity error: Two corners or edges are swapped, which is not physically possible.")
            else:
                print(f"[!] Invalid cube input: {e}")
            sys.exit(1)
        except RuntimeError as e:
            print(f"[!] Error: {e}")
            sys.exit(1)

    else:
        visualizer = CubeVisualizer()

    visualizer.run()


if __name__ == "__main__":
    main()