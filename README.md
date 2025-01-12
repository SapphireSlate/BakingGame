# Baking Game

An advanced baking simulation game built with Pygame.

## Installation

### From GitHub Release (Recommended)
1. Go to the [Releases](https://github.com/yourusername/baking-game/releases) page
2. Download the latest release for your operating system
3. Extract the archive and run the executable

### From Source
```bash
# Clone the repository
git clone https://github.com/yourusername/baking-game.git
cd baking-game

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the game
pip install -e .

# Run the game
baking-game
```

## Development Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/baking-game.git
cd baking-game

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run the game directly
python baking_game.py
```

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