#!/usr/bin/env python3
"""
Rubik's Cube Solver

"""

import sys
import os
import time
import argparse

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from twophase import solve, solve_best, solve_best_generator


def main():

    parser = argparse.ArgumentParser(description="Rubik's Cube Solver using Two-Phase Algorithm")
    parser.add_argument("--cube", required=True, help="The cube state as a 54-character string")
    parser.add_argument("--max-length", type=int, default=25, help="Maximum solution length")
    parser.add_argument("--max-time", type=float, default=10.0, help="Maximum solving time in seconds")
    
    parser.add_argument(
        "--method", 
        choices=["first", "best", "all"], 
        default="first",
        help="Solving method: 'first' finds the first solution, 'best' finds the shortest solution, 'all' shows all solutions as they're found"
    )
    
    args = parser.parse_args()
    
    try:
        cube_string = args.cube
        if len(cube_string) != 54:
            raise ValueError("Cube string must be 54 characters long")
        print(f"Solving cube: {cube_string}")
        print(f"Max length: {args.max_length}, Max time: {args.max_time} seconds")
        print(f"Method: {args.method}")
        
        start_time = time.time()
        
        if args.method == "first":
            solution = solve(cube_string, args.max_length, args.max_time)
            solve_time = time.time() - start_time
            
            print("\nSolution found!")
            print(f"Moves: {solution}")
            print(f"Number of moves: {len(solution.split())}")
            print(f"Solving time: {solve_time:.2f} seconds")
            
        elif args.method == "best":
            solutions = solve_best(cube_string, args.max_length, args.max_time)
            solve_time = time.time() - start_time
            
            if solutions:
                best_solution = solutions[-1] 
                print("\nBest solution found!")
                print(f"Moves: {best_solution}")
                print(f"Number of moves: {len(best_solution.split())}")
                print(f"Total solutions found: {len(solutions)}")
                print(f"Solving time: {solve_time:.2f} seconds")
                
                if len(solutions) > 1:
                    print("\nAll solutions (from longest to shortest):")
                    for i, sol in enumerate(solutions):
                        print(f"{i+1}. {sol} ({len(sol.split())} moves)")
            else:
                print("\nNo solutions found within the time limit.")
                
        elif args.method == "all":
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



