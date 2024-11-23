import json
import os
from game_state import Game
from animation import AnimationManager

def save_game(game):
    save_data = {
        "bakecoin": game.bakecoin,
        "discovered_recipes": list(game.discovered_recipes),
        "achievements": game.achievements,
        "difficulty": game.difficulty,
        "disaster_count": game.disaster_count,
        "has_baked": game.has_baked
    }
    with open("savegame.json", "w") as f:
        json.dump(save_data, f)

def load_game():
    try:
        with open("savegame.json", "r") as f:
            save_data = json.load(f)
        animation_manager = AnimationManager()  # Create animation manager
        game = Game(animation_manager)  # Pass animation manager to Game
        game.load_from_save(save_data)
        return game
    except FileNotFoundError:
        animation_manager = AnimationManager()  # Create animation manager
        return Game(animation_manager)  # Pass animation manager to Game

def clear_saved_game():
    if os.path.exists("savegame.json"):
        os.remove("savegame.json")
        print("Saved game data cleared.")
    else:
        print("No saved game data found.")
