# Snake Game
## Description

This project creates a simple and visually appealing Snake game using the Python pygame library. The player controls a snake that moves across a grid, collecting apples to grow longer while avoiding collisions with the walls or its own body. The game includes a clean interface with a score display, adjustable speed settings, and both keyboard and on-screen controls.

The program demonstrates basic concepts in Python game development, including:

- Drawing shapes and UI elements using Pygame
- Using functions to organize and modularize code
- Handling keyboard and mouse input
- Implementing game loops and timed events
- Collision detection and grid-based movement
Code Overview

The project is structured around reusable functions:

- draw_snake(surf, snake, direction, panel_h) – Draws the snake with a head and body segments, including directional details like eyes.
- draw_apple(surf, food, panel_h) – Draws the apple that the snake collects.
- draw_board(surf, panel_h) – Creates the grid-based game background.
- place_food(snake) – Randomly generates a new apple position that does not overlap with the snake.
- change_dir(cur, nxt, dx, dy) – Updates the snake’s direction while preventing it from reversing into itself.

The main game loop updates the snake’s position, checks for collisions, handles scoring, and redraws the screen continuously. Random apple placement and player input make each playthrough slightly different, creating an engaging gameplay experience.
