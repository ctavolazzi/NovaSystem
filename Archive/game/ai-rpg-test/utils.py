# utils.py

import os

def ensure_game_directory(game_id, subdirectory=None):
    """Ensure the game directory and optional subdirectory exist."""
    game_dir = f"Games/game_{game_id}"
    if subdirectory:
        game_dir = os.path.join(game_dir, subdirectory)
    os.makedirs(game_dir, exist_ok=True)
    return game_dir