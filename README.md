_This project has been created as part of the 42 curriculum by @jperez-s & @josjimen_

#Description

    A-MAZE-ING in a Python program that creates mazes using maze generation algorithms and displays them via a graphical interface. 

    The maze is generated using patameters provided in a configuration file. 
    This program supports different algorithms and ensures the presence of a 42 pattern in the center of the maze. 

    This application also provides an interactive visualization where the user can explore the generated maze. 

#Project Goal

    The goal of this project is to:
    - Implement maze generation algorithms
    - Parse and validate configuration files
    - Generate deterministic mazes using seeds
    - Display the maze usinng a graphical interface
    - Integrate a fixed 42-shaped structure inside the maze

#Installation

    Clone the repository and install dependencies:
        git clone <repository_url>
        cd A_MAZE_ING
        make install
    The install rule will create a Pyhton virtual environment, upgrade pip and install required dependencies.

#Running the program

    The file requires a configuration file, which is provided.
    Example usage: python3 a_maze_ing.py config.txt
    or using the Makefile: make run

#Configuration File

    The maze behaviour is controlled with a configuration file. Example:

    WIDTH=30
    HEIGHT=30
    ENTRY=0,0
    EXIT=29,29
    OUTPUT_FILE=maze.txt
    PERFECT=True
    SEED=18
    ALGORITHM=prim

#Configuration Parameters

    Parameter ----- Description
    WIDTH --------- Width of the maze
    HEIGHT -------- Height of the maze
    ENTRY --------- Starting coordinate (x,y)
    EXIT ---------- Exit coordinate (x,y)
    OUTPUT_FILE --- Output file for the generated maze
    PERFECT	------- Enables perfect maze generation
    SEED ---------- Seed used for deterministic generation
    ALGORITHM ------ Maze generation algorithm

#Supported Algorithms

    The project supports the following maze generation algorithms:

    - Prim

    - Depth-First Search (aka dfs)

    - Kruskal

    Each algorithm produces a different maze structure while respecting the constraints of the project.

#Controls

    During visualization the following controls are available:

    Key -------------------- Action
    Arrow Keys / WASD ------ Move inside the maze
    R ---------------------- Generate a new maze
    Q ---------------------- Quit the program
    L ---------------------- Open leaderboard (only in Heart mode)
    C ---------------------- Changes the colour palette

#Makefile

#Project Structure

    .
    ├── a_maze_ing.py
    ├── config
    │   └── parser_config.py
    ├── mazegen
    │   └── generator.py
    ├── display.py
    ├── mlx
    ├── requirements.txt
    ├── Makefile
    └── README.md

#Team Responsabilities

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

#Notes

    - The maze always includes a 42-shaped wall pattern located in the center.

    - The configuration parser prevents invalid starting positions inside this pattern.

    - The graphical interface is implemented using MiniLibX.

#Bonus Features

    - Multiple maze generation algorithms
    - Animated victory screen
    - Step counter
    - Time counter
    - Heart-shapped custom map
    - Scores and leaderboard