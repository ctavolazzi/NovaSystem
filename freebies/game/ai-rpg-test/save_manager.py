import json
import os
import glob
import logging

class SaveManager:
    @staticmethod
    def save_game_state(game_id, current_node_id, player_character):
        data = {
            "current_node_id": current_node_id,
            "player_character_id": player_character.id
        }
        os.makedirs(f"Games/game_{game_id}", exist_ok=True)
        with open(f"Games/game_{game_id}/game_{game_id}.json", "w") as file:
            json.dump(data, file)

    @staticmethod
    def load_game_state(game_id):
        file_path = f"Games/game_{game_id}/game_{game_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
        return None

    @staticmethod
    def get_saved_games():
        return glob.glob("Games/game_*/game_*.json")

    @staticmethod
    def generate_game_id():
        save_path = 'saves/'
        existing_games = glob.glob(os.path.join(save_path, 'game_*.json'))
        logging.info(f"Existing games: {existing_games}")

        if not existing_games:
            return 1

        game_ids = []
        for g in existing_games:
            try:
                game_id = int(g.split("_")[1].split(".")[0])
                game_ids.append(game_id)
            except ValueError:
                logging.warning(f"Invalid game file format: {g}")

        if not game_ids:
            return 1

        last_game_id = max(game_ids)
        return last_game_id + 1
