_This project has been created as part of the 42 curriculum by @jperez-s & @josjimen_

# Description

    A-MAZE-ING in a Python program that creates mazes using maze generation algorithms and displays them via a graphical interface. 

    The maze is generated using patameters provided in a configuration file. 
    This program supports different algorithms and ensures the presence of a 42 pattern in the center of the maze. 

    This application also provides an interactive visualization where the user can explore the generated maze. 

# Project Goal

    The goal of this project is to:
    - Implement maze generation algorithms
    - Parse and validate configuration files
    - Generate deterministic mazes using seeds
    - Display the maze usinng a graphical interface
    - Integrate a fixed 42-shaped structure inside the maze

# Installation

    Clone the repository and install dependencies:
        git clone <repository_url>
        cd A_MAZE_ING
        make install
    The install rule will create a Pyhton virtual environment, upgrade pip and install required dependencies.

# Running the program

    The file requires a configuration file, which is provided.
    Example usage: python3 a_maze_ing.py config.txt
    or using the Makefile: make run

# Configuration File

    The maze behaviour is controlled with a configuration file. Example:

    WIDTH=30
    HEIGHT=30
    ENTRY=0,0
    EXIT=29,29
    OUTPUT_FILE=maze.txt
    PERFECT=True
    SEED=18 # OPTIONAL PARAMETER
    ALGORITHM=prim # OPTIONAL PARAMETER

# Controls

    During visualization the following controls are available:

    Key -------------------- Action
    Arrow Keys / WASD ------ Move inside the maze
    R ---------------------- Generate a new maze
    Q/ESC ------------------ Quit the program
    L ---------------------- Open leaderboard (only in Heart mode)
    P ---------------------- Show the shortest solution/path
    C ---------------------- Changes the colour palette

# Configuration Parameters

    Parameter ----- Description
    WIDTH --------- Width of the maze
    HEIGHT -------- Height of the maze
    ENTRY --------- Starting coordinate (x,y)
    EXIT ---------- Exit coordinate (x,y)
    OUTPUT_FILE --- Output file for the generated maze
    PERFECT	------- Enables perfect maze generation
    SEED ---------- Seed used for deterministic generation
    ALGORITHM ----- Maze generation algorithm

# Re-usable Module

    The maze generation logic is implemented in a standalone module called mazegen.
    It provides a MazeGenerator class that can be reused in other Python projects.

## Basic usage

    from mazegen import MazeGenerator

    gen = MazeGenerator(width=20, height=10, seed=42)
    maze = gen.generate()

## Custom parameters

    The generator can receive parameters such as maze size or a random seed to ensure reproducibility.

## Accessing the result

    The module exposes the generated maze structure and allows access to a valid solution path from entry to exit.

# Supported Algorithms

    The project supports the following maze generation algorithms:

    - prim: chosen for its ability to generate well-balanced mazes with a natural distribution of paths.


    - dfs: selected for its simplicity and efficiency, producing mazes with long corridors and clear exploration flow.

    - kruskal: included to demonstrate an alternative approach based on graph theory and disjoint sets.

    Each algorithm produces a different maze structure while respecting the constraints of the project.

# Makefile

    The project includes a Makefile to automate common development tasks such as environment setup, running the application, linting, debugging, and packaging.

## install
    Creates the Python virtual environment and installs all required dependencies.
        make install
    This command will:
    - create the venv virtual environment
    - upgrade pip
    - install dependencies from requirements.txt
    - install the project in editable mode

## run

    Runs the maze generator using the default configuration file.
        make run
    Equivalent to:
        python3 a_maze_ing.py config.txt

## debug
    
    Runs the program using the Python debugger (pdb).
        make debug
    Useful for step-by-step debugging and inspecting program state during execution.

## lint
    
    Runs code quality checks using flake8 and mypy.
        make lint
    This performs:
        - style checking with flake8
        - static type analysis with mypy
    The mlx directory is excluded from type checking since it contains external bindings.

## lin-strict

    Runs stricter static analysis using mypy's strict mode.
        make lint-strict
    This mode enforces stricter type checking rules during development.

## package

    Builds the project as a distributable Python package.
        make package
    This uses python -m build to generate package artifacts in the dist/ directory.

## clean

    Removes generated files and development artifacts.
        make clean
    This command deletes:
        - Python cache directories (__pycache__)
        - .mypy_cache
        - virtual environment (venv)
        - build artifacts (build, dist)
        - package metadata (*.egg-info)


# Resources

    During the development of this project, several external resources were consulted to better understand algorithms, tools, and technical concepts. These resources were used strictly for learning and clarification purposes.

## Peer Learning

    Discussions with other students who had already completed or submitted the project helped clarify implementation approaches and common pitfalls.

    Informal peer-to-peer exchanges were used to validate ideas and understand the project requirements more clearly.

## Open Source References

    Public GitHub repositories from fellow students were reviewed to understand different structural approaches to the project.
     - @cpadron-: https://github.com/cpadronrz
     - acaire-d: https://github.com/AnaisCaire

## Documentation and Articles

    Several technical references were consulted to understand the theoretical background of maze generation algorithms and related concepts:

        - Wikipedia articles on maze generation algorithms

        - Stack Overflow discussions related to Python implementation details and debugging

## Video Tutorials

    Educational YouTube videos were used to better understand:
        - Maze generation algorithms
        - Graph traversal techniques
        - Conceptual explanations of Prim's, DFS, and Kruskal's algorithms

## AI Assistance

    AI tools (ChatGPT) were used as a learning aid to:

        - clarify specific programming doubts
        - review potential errors
        - better understand certain concepts related to MiniLibX where documentation was limited or incomplete
        - formatting the README file

    The final implementation and design decisions were developed and written by the project authors.


# Learnings: what worked and what didn't

    This project provided valuable experience not only in algorithm implementation, but also in team collaboration, project organization, and development workflow.

## What worked well
    - Fluid communication within the team allowed us to quickly resolve doubts and coordinate development tasks.

    - We organized a dedicated brainstorming session to explore possible bonus features and define the overall direction of the project.

    - Responsibilities were initially split between team members and later adjusted dynamically based on development progress and workload.

    - We significantly improved our Git workflow, including the use of branching, committing, and merging strategies to coordinate development.

    - Time was invested in designing validation rules and testing edge cases, which helped ensure the robustness of the configuration parser and error handling.

## Challenges and limitations
    - Some planned bonus features had to be discarded due to time constraints, as we prioritized completing and stabilizing the core functionality of the project.

    - We encountered difficulties when attempting to run the project on a personal Ubuntu server without a graphical display environment, which revealed the limitations of running MiniLibX-based applications in headless systems.

    - The MiniLibX version initially provided with the subject lacked certain functionality, which required additional research and the integration of a more stable version of the library into the project.

# Project Structure

    .
    ├── a_maze_ing.py
    ├── config/
    │   └── parser_config.py
    ├── config.txt
    ├── mazegen/
    │   └── generator.py
    ├── display.py
    ├── mlx/
    ├── test/
    ├── requirements.txt
    ├── Makefile
    ├── pyproject.toml
    └── README.md

# Team Responsabilities

    @jperez-s main contributions:
    - Maze generation algorithms implementation
    - Internal maze representation
    - Integration of the 42 pattern within the maze
    - Graphical rendering and visualization
    - Player interaction and movement system
    - Animation and game interface

    @josjimen main contributions:
    - Configuration file parsing
    - Input validation and error handling
    - Imlementation of configuration rules
    - Test generation and validation scenarios
    - Project documentation
    - Repository organization and project structure

    Collaboration:
    - Debugging and testing the full application
    - Ensuring integration between modules
    - Reviewing implementation decisions
    - Final validation of project requirements

# Bonus Features

    - Multiple maze generation algorithms
        Supports different generation strategies (Prim, DFS, Kruskal), producing varied maze structures.
    - Animated victory screen
        Displays an animated end screen when the player reaches the exit.
    - Step counter
        Tracks the number of moves taken by the player to complete the maze.
    - Time counter
        Measures the time required to reach the exit.
    - Heart-shapped custom map
        Includes an alternative maze layout featuring a heart-shaped structure.
    - Scores and leaderboard
        Stores and displays the top 5 scores based on time and steps, exclusively for the heart-shapped custom map.


# Notes

    - The maze always includes a 42-shaped wall pattern located in the center.

    - The configuration parser prevents invalid starting positions inside this pattern.

    - The graphical interface is implemented using MiniLibX.

