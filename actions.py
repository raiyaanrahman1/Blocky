"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

=== Module Description ===

This file contains the different actions that can be made by a Player.
"""
import pygame

# Actions that can be performed in the game
ROTATE_CLOCKWISE = ('rotate', 1)
ROTATE_COUNTER_CLOCKWISE = ('rotate', 3)
SWAP_HORIZONTAL = ('swap', 0)
SWAP_VERTICAL = ('swap', 1)
SMASH = ('smash', None)
COMBINE = ('combine', None)
PAINT = ('paint', None)
PASS = ('pass', None)

ACTION_LABEL = {
    ROTATE_CLOCKWISE: 'Rotate Clockwise',
    ROTATE_COUNTER_CLOCKWISE: 'Rotate Counterclockwise',
    SWAP_HORIZONTAL: 'Swap Horizontally',
    SWAP_VERTICAL: 'Swap Vertically',
    SMASH: 'Smash Block',
    COMBINE: 'Combine Blocks',
    PAINT: 'Paint Blocks',
    PASS: 'Pass'
}

ACTION_MESSAGE = {
    ROTATE_CLOCKWISE: 'rotating a block clockwise',
    ROTATE_COUNTER_CLOCKWISE: 'rotating a block counter-clockwise',
    SWAP_HORIZONTAL: 'swapping a block horizontally',
    SWAP_VERTICAL: 'swapping a block vertically',
    SMASH: 'smashing a block',
    COMBINE: 'combining blocks',
    PAINT: 'painting blocks',
    PASS: 'passing'
}

ACTION_PENALTY = {
    ROTATE_CLOCKWISE: 0,
    ROTATE_COUNTER_CLOCKWISE: 0,
    SWAP_HORIZONTAL: 0,
    SWAP_VERTICAL: 0,
    SMASH: 3,
    COMBINE: 1,
    PAINT: 1,
    PASS: 0
}

ACTION_KEY = {
    ROTATE_CLOCKWISE: pygame.K_d,
    ROTATE_COUNTER_CLOCKWISE: pygame.K_a,
    SWAP_HORIZONTAL: pygame.K_q,
    SWAP_VERTICAL: pygame.K_e,
    SMASH: pygame.K_SPACE,
    COMBINE: pygame.K_c,
    PAINT: pygame.K_r,
    PASS: pygame.K_TAB
}

# Create a dictionary that is ACTION_KEY inverted
KEY_ACTION = {value: key for key, value in ACTION_KEY.items()}
