# Rubik's Cube Solver

A Python-based Rubik's Cube solver and visualizer that uses the Two-Phase Algorithm to find optimal solutions for any valid cube configuration.

## Features

- **Powerful Solver**: Uses Herbert Kociemba's Two-Phase Algorithm to find optimal or near-optimal solutions
- **3D Visualization**: Interactive 3D visualization of the cube using PyGame and OpenGL
- **Animation**: Animated solution playback
- **Command-line Interface**: Solve cubes directly from the command line
- **Multiple Solving Methods**: Find first solution, best solution, or all solutions

## Installation

### Prerequisites

- Python 3.6 or higher
- PyGame
- PyOpenGL
- NumPy

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rubiks-cube-solver.git
   cd rubiks-cube-solver
   ```

2. Install the required dependencies:
   ```
   pip install pygame pyopengl numpy
   ```

## Usage

### Cube Visualizer

Run the visualizer with a specific cube configuration:

```
python cube_visualizer.py --cube DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL
```

The cube string should be a 54-character string representing the colors on each face in the following order:
- U (Up): positions 0-8
- R (Right): positions 9-17
- F (Front): positions 18-26
- D (Down): positions 27-35
- L (Left): positions 36-44
- B (Back): positions 45-53

### Controls

- **Left Mouse Button**: Rotate the cube view
- **R Key**: Reset the cube to its initial state
- **Space**: Pause/resume animation
- **ESC**: Quit the application

### Command-line Solver

Solve a cube without visualization:

```
python solve_rubiks.py --cube DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL
```

Additional options:
- `--max-length`: Maximum solution length (default: 30)
- `--max-time`: Maximum solving time in seconds (default: 10.0)
- `--method`: Solving method - 'first', 'best', or 'all' (default: 'first')

Example:
```
python solve_rubiks.py --cube DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL --method best --max-time 20
```
Solve a cube with visualization:

```
python cube_visualizer.py --cube DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL
```

## Cube Notation

The solver uses standard cube notation:
- `F`: Front face clockwise
- `F'`: Front face counter-clockwise
- `F2`: Front face 180 degrees
- Similarly for other faces: `U` (Up), `R` (Right), `D` (Down), `L` (Left), `B` (Back)

## Color Scheme

The standard color scheme is:
- `U`: White (Up)
- `R`: Red (Right)
- `F`: Green (Front)
- `D`: Yellow (Down)
- `L`: Orange (Left)
- `B`: Blue (Back)

## How It Works

The solver implements Herbert Kociemba's Two-Phase Algorithm:

1. **Phase 1**: Transforms the cube to a state where all edges are oriented correctly, all corners are oriented correctly, and the UD-slice edges are in the UD-slice
2. **Phase 2**: Solves the remaining cube using only half-turn moves of the Up and Down faces, and quarter or half turns of the other faces

The algorithm uses pattern databases (pruning tables) to efficiently search for solutions.

## Project Structure

- `solve_rubiks.py`: Command-line interface for solving cubes
- `cube_visualizer.py`: 3D visualization of the cube and solutions
- `twophase/`: Implementation of the Two-Phase Algorithm
  - `__init__.py`: Main solver interface
  - `solve.py`: Core solving logic
  - `tables.py`: Pruning tables for efficient solving
  - `cubes/`: Cube representation classes
    - `cubiecube.py`: Internal representation of the cube
    - `facecube.py`: Face-based representation of the cube
    - `coordcube.py`: Coordinate-based representation for the solver
- `pieces.py`: Enumerations for cube faces, corners, and edges
- `random.py`: Generates random cube states
