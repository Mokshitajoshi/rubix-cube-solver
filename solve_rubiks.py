#!/usr/bin/env python3
"""
Standalone Rubik's Cube Solver

This script can be run directly from the command line to solve a Rubik's cube.
"""

import sys
import os
import time
import argparse

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import the necessary modules
from twophase import solve, solve_best, solve_best_generator


def main():
    """
    Main function to handle command-line arguments and solve the cube.
    """
    parser = argparse.ArgumentParser(description="Rubik's Cube Solver using Two-Phase Algorithm")
    parser.add_argument("--cube", required=True, help="The cube state as a 54-character string")
    parser.add_argument("--max-length", type=int, default=25, help="Maximum solution length")
    parser.add_argument("--max-time", type=float, default=10.0, help="Maximum solving time in seconds")
    
    # Add option for solve method
    parser.add_argument(
        "--method", 
        choices=["first", "best", "all"], 
        default="first",
        help="Solving method: 'first' finds the first solution, 'best' finds the shortest solution, 'all' shows all solutions as they're found"
    )
    
    args = parser.parse_args()
    
    try:
        cube_string = args.cube
        
        # Solve the cube
        print(f"Solving cube: {cube_string}")
        print(f"Max length: {args.max_length}, Max time: {args.max_time} seconds")
        print(f"Method: {args.method}")
        
        start_time = time.time()
        
        if args.method == "first":
            # Find the first solution
            solution = solve(cube_string, args.max_length, args.max_time)
            solve_time = time.time() - start_time
            
            print("\nSolution found!")
            print(f"Moves: {solution}")
            print(f"Number of moves: {len(solution.split())}")
            print(f"Solving time: {solve_time:.2f} seconds")
            
        elif args.method == "best":
            # Find the best (shortest) solution
            solutions = solve_best(cube_string, args.max_length, args.max_time)
            solve_time = time.time() - start_time
            
            if solutions:
                best_solution = solutions[-1]  # Last solution is the shortest
                print("\nBest solution found!")
                print(f"Moves: {best_solution}")
                print(f"Number of moves: {len(best_solution.split())}")
                print(f"Total solutions found: {len(solutions)}")
                print(f"Solving time: {solve_time:.2f} seconds")
                
                # Print all solutions if there are multiple
                if len(solutions) > 1:
                    print("\nAll solutions (from longest to shortest):")
                    for i, sol in enumerate(solutions):
                        print(f"{i+1}. {sol} ({len(sol.split())} moves)")
            else:
                print("\nNo solutions found within the time limit.")
                
        elif args.method == "all":
            # Show all solutions as they're found
            print("\nSearching for solutions (press Ctrl+C to stop)...")
            count = 0
            try:
                for solution in solve_best_generator(cube_string, args.max_length, args.max_time):
                    count += 1
                    current_time = time.time() - start_time
                    print(f"\nSolution {count} found after {current_time:.2f} seconds:")
                    print(f"Moves: {solution}")
                    print(f"Number of moves: {len(solution.split())}")
                
                solve_time = time.time() - start_time
                print(f"\nSearch completed in {solve_time:.2f} seconds.")
                print(f"Total solutions found: {count}")
                
            except KeyboardInterrupt:
                solve_time = time.time() - start_time
                print(f"\nSearch interrupted after {solve_time:.2f} seconds.")
                print(f"Total solutions found: {count}")
        
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except RuntimeError as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())



