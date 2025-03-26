import pygame
import math
import random

# Cube configuration
WIDTH, HEIGHT = 800, 600
FOV = 500  # Field of view
CUBE_SIZE = 3  # 3x3x3 cube
CUBIE_SIZE = 1
COLORS = {
    'U': (255, 255, 255),  # White
    'D': (255, 255, 0),   # Yellow
    'F': (255, 0, 0),     # Red
    'B': (255, 128, 0),   # Orange
    'L': (0, 255, 0),     # Green
    'R': (0, 0, 255)      # Blue
}

class Cubie:
    def __init__(self, x, y, z, colors):
        self.position = [x, y, z]
        self.colors = colors  # { 'U': color, 'F': color, ... }

    def rotate(self, axis, angle):
        """Rotate cubie around given axis (x/y/z) by angle (radians)."""
        angle = math.radians(angle)
        if axis == 'x':
            rot_mat = [
                [1, 0, 0],
                [0, math.cos(angle), -math.sin(angle)],
                [0, math.sin(angle), math.cos(angle)]
            ]
        elif axis == 'y':
            rot_mat = [
                [math.cos(angle), 0, math.sin(angle)],
                [0, 1, 0],
                [-math.sin(angle), 0, math.cos(angle)]
            ]
        elif axis == 'z':
            rot_mat = [
                [math.cos(angle), -math.sin(angle), 0],
                [math.sin(angle), math.cos(angle), 0],
                [0, 0, 1]
            ]
        self.position = [
            sum([self.position[j] * rot_mat[i][j] for j in range(3)])
            for i in range(3)
        ]

class RubiksCube3D:
    def __init__(self):
        self.cubies = []
       
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                for z in (-1, 0, 1):
                    if x == 0 and y == 0 and z == 0:
                        continue  
                    colors = {}
                    if x == 1: colors['R'] = COLORS['R']
                    if x == -1: colors['L'] = COLORS['L']
                    if y == 1: colors['U'] = COLORS['U']
                    if y == -1: colors['D'] = COLORS['D']
                    if z == 1: colors['F'] = COLORS['F']
                    if z == -1: colors['B'] = COLORS['B']
                    self.cubies.append(Cubie(x, y, z, colors))
        self.angle_x = 0
        self.angle_y = 0

    def rotate_global(self, axis, angle):
        """Rotate entire cube around global axis."""
        for cubie in self.cubies:
            cubie.rotate(axis, angle)

    def project(self, cubie):
        """Project 3D cubie position to 2D screen coordinates."""
        x, y, z = cubie.position
        # Perspective projection
        factor = FOV / (FOV + z)
        screen_x = int(WIDTH/2 + x * factor * CUBE_SIZE * 30)
        screen_y = int(HEIGHT/2 + y * factor * CUBE_SIZE * 30)
        size = CUBIE_SIZE * factor * 30
        return (screen_x, screen_y, size)

    def get_visible_faces(self, cubie):
        """Determine which faces of a cubie are visible."""
        x, y, z = cubie.position
        visible = []
        if z > 0: visible.append('F')
        if z < 0: visible.append('B')
        if x > 0: visible.append('R')
        if x < 0: visible.append('L')
        if y > 0: visible.append('U')
        if y < 0: visible.append('D')
        return visible

    def draw(self, screen):
        """Draw sorted cubies with perspective."""
        # Sort cubies by depth (z position)
        sorted_cubies = sorted(self.cubies, key=lambda c: -c.position[2])
        
        for cubie in sorted_cubies:
            projected = self.project(cubie)
            if projected[2] <= 0:
                continue  # Skip cubies behind camera
            
            # Draw visible faces
            for face in self.get_visible_faces(cubie):
                color = cubie.colors.get(face, (0, 0, 0))
                rect = pygame.Rect(projected[0]-projected[2]/2,
                                   projected[1]-projected[2]/2,
                                   projected[2],
                                   projected[2])
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0,0,0), rect, 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    cube = RubiksCube3D()
    drag = False
    prev_mouse = (0, 0)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                drag = True
                prev_mouse = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                drag = False
            elif event.type == pygame.MOUSEMOTION and drag:
                dx, dy = pygame.mouse.get_rel()
                cube.angle_y += dx * 0.5
                cube.angle_x -= dy * 0.5
                cube.rotate_global('y', dx * 0.5)
                cube.rotate_global('x', -dy * 0.5)

        screen.fill((128, 128, 128))
        cube.draw(screen)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()