# Baking Game

A Python-based cooking simulation game where players can mix ingredients, discover recipes, and earn Bakecoin.

## Overview

This game is built using Pygame and features:
- Real-time ingredient mixing and baking mechanics
- Recipe discovery system
- Economy system with Bakecoin currency
- Multiple difficulty levels
- Modern UI with visual feedback
- Upgrade system for kitchen improvements

## Requirements

- Python 3.12+
- Pygame 2.6.1+
- SDL 2.28.4+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SapphireSlate/BakingGame.git
cd BakingGame
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python baking_game.py
```

## How to Play

1. Start the game and press ENTER
2. Choose difficulty level:
   - E: Easy (100 Bakecoin start)
   - N: Normal (75 Bakecoin start)
   - H: Hard (50 Bakecoin start)
3. Click ingredients to add them to the mixing bowl
4. Press ENTER to bake when ready
5. Discover new recipes and earn Bakecoin
6. Purchase upgrades to improve your kitchen

## Known Issues

### Current Problems

1. Game State Transition Issue:
   - The game sometimes fails to properly transition to the main game state after selecting difficulty
   - Error message: "Error in game loop: invalid color argument"
   - Status: Under investigation, related to color handling in UI components

2. Color Handling:
   - Some UI elements experience issues with color arguments
   - Affects various game screens and transitions
   - Current fix attempt: Updated color handling to use consistent RGBA format

### Workarounds

- If the game gets stuck at the difficulty selection screen, try restarting the game
- If UI elements appear incorrectly colored, restart the game

## Development Status

The game is currently in active development. Major features are implemented but some stability issues need to be resolved.

### Recent Changes

- Added proper RGBA color handling throughout the UI system
- Updated sprite color management
- Improved state transition handling
- Fixed particle system color formats

### Planned Improvements

- Resolve state transition issues
- Stabilize UI rendering
- Add more recipes and ingredients
- Implement save/load system
- Add sound effects and background music

## Contributing

Feel free to submit issues and enhancement requests. We welcome contributions to improve the game.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 