import json
import hashlib
import ollama
import os
import glob
from pyfiglet import Figlet
from termcolor import colored
from colorama import init
import logging
import uuid

# Initialize colorama
init(strip=not os.sys.stdout.isatty())

# Add this at the top of your game.py file
logging.basicConfig(level=logging.INFO)

from utils import ensure_game_directory
from ai_manager import AIManager
from character import Character
from item import Item
from loot import Loot
from story_node import StoryNode
from story_tree import StoryTree, TreeNode
from save_manager import SaveManager
from story_arc import StoryArc

class Game:
    def __init__(self):
        self.ai_manager = AIManager()
        self.story_arc = StoryArc()
        self.player_character = None
        self.current_node = None
        self.story_tree = None
        self.game_id = None
        self.save_manager = SaveManager()
        self.character_id_counter = 0

    def write_to_file(self, filename, content):
        os.makedirs(f"game_logs/{self.game_id}", exist_ok=True)
        file_path = f"game_logs/{self.game_id}/{filename}"
        with open(file_path, 'w', encoding='utf-8') as f:
            if isinstance(content, dict):
                json.dump(content, f, indent=2)
            else:
                f.write(str(content))
        print(f"Wrote content to {file_path}")

    def generate_character_id(self):
        self.character_id_counter += 1
        return f"char_{self.character_id_counter}"

    def start(self):
        self._display_banner()
        self._initial_prompt()

    def _display_banner(self):
        banner = Figlet(font='slant')
        print(colored(banner.renderText('AI RPG Adventure'), 'cyan'))
        print(colored("Welcome to the AI-generated RPG adventure!", 'green'))

    def _initial_prompt(self):
        print("1. Start a New Game")
        print("2. Load a Saved Game")
        choice = input("> ")

        if choice == "1":
            self._new_game()
        elif choice == "2":
            self._load_saved_game()
        else:
            print("Invalid choice. Please enter 1 or 2.")
            self._initial_prompt()

    def _new_game(self):
        logging.info("Starting a new game")
        print("Choose your starting scenario:")
        print("1. Village Hero")
        print("2. Wandering Mage")
        print("3. Rogue Outcast")
        scenario_choice = input("> ")

        if scenario_choice == "1":
            self.starting_scenario = "Village Hero"
        elif scenario_choice == "2":
            self.starting_scenario = "Wandering Mage"
        elif scenario_choice == "3":
            self.starting_scenario = "Rogue Outcast"
        else:
            print("Invalid choice. Defaulting to Village Hero.")
            self.starting_scenario = "Village Hero"

        logging.info(f"Selected scenario: {self.starting_scenario}")

        print("What is your character's name?")
        name = input("> ")
        character_id = self.generate_character_id()
        self.player_character = Character(character_id, name, "The player character", {"class": self.starting_scenario})
        logging.info(f"Created player character: {name}, ID: {character_id}")

        self.game_id = SaveManager.generate_game_id()
        logging.info(f"Generated game ID: {self.game_id}")

        logging.info(f"Calling ensure_game_directory with game_id: {self.game_id}")
        ensure_game_directory(self.game_id)
        logging.info("ensure_game_directory called successfully")

        self.player_character.save_to_file(self.game_id)
        logging.info("Player character saved to file")

        self._generate_story_node()
        logging.info("Generated initial story node")

        self._game_loop()

    def _load_saved_game(self):
        saved_games = SaveManager.get_saved_games()
        if not saved_games:
            print("No saved games found. Starting a new game.")
            self._new_game()
            return

        print("Saved Games:")
        for i, game in enumerate(saved_games, 1):
            print(f"{i}. {game}")

        print("Enter the number of the game you want to load:")
        choice = input("> ")

        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(saved_games):
                self.game_id = int(saved_games[choice_index].split("_")[1].split(".")[0])
                self._confirm_load_game()
            else:
                print("Invalid choice. Please try again.")
                self._load_saved_game()
        except ValueError:
            print("Invalid choice. Please enter a valid number.")
            self._load_saved_game()

    def _confirm_load_game(self):
        print("Are you sure you want to load this game? (Y/N)")
        confirmation = input("> ")

        if confirmation.lower() == "y":
            self._load_game_state()
            self._game_loop()
        elif confirmation.lower() == "n":
            self._load_saved_game()
        else:
            print("Invalid choice. Please enter Y or N.")
            self._confirm_load_game()

    def _generate_story_node(self):
        context = self._build_context()
        self.write_to_file("context.json", context)

        # Generate title
        title_data = self.ai_manager.generate_title(context)
        title = title_data.get("title", "Untitled Node")

        # Generate main text
        text_data = self.ai_manager.generate_main_text(context)
        text = text_data.get("text", "No text available.")

        # Generate choices
        choices_data = self.ai_manager.generate_choices(context)
        choices = choices_data.get("choices", ["Continue"])

        # Generate characters
        characters_data = self.ai_manager.generate_characters(context)
        characters = []
        for char_data in characters_data.get("characters", []):
            char_id = self.generate_character_id()
            characters.append(Character(char_id, char_data["name"], char_data["description"], {}))

        # Generate items
        items_data = self.ai_manager.generate_items(context)
        items = [Item(item.get("id", ""), item.get("name", ""), item.get("description", ""), item.get("effect", "")) 
                 for item in items_data.get("items", [])]

        # Generate loot
        loot_data = self.ai_manager.generate_loot(context)
        loot = [Loot(loot.get("id", ""), loot.get("name", ""), loot.get("description", ""), loot.get("attributes", {})) 
                for loot in loot_data.get("loot", [])]

        # Create new node
        new_node = StoryNode(
            id=self.story_tree.generate_new_node_id() if self.story_tree else str(uuid.uuid4()),
            title=title,
            text=text,
            choices=choices,
            characters=characters,
            items=items,
            loot=loot
        )
        self.write_to_file(f"node_{new_node.id}.json", new_node.to_dict())

        if not self.story_tree:
            self.story_tree = StoryTree(TreeNode(new_node))
        else:
            parent_id = self.current_node.id if self.current_node else self.story_tree.root.id
            new_tree_node = TreeNode(new_node)
            self.story_tree.add_node(new_tree_node, parent_id)

        self.current_node = new_node
        self.save_manager.save_game_state(self.game_id, self.current_node.id, self.player_character)

        # Write the entire story tree to a file
        self.write_to_file("story_tree.json", self.story_tree.to_dict())

    def _build_context(self):
        return {
            "player_name": self.player_character.name,
            "player_class": self.player_character.attributes['class'],
            "current_situation": self.current_node.text if self.current_node else "Starting the adventure",
            "previous_choice": self.current_node.choices[self.last_choice_index] if hasattr(self, 'last_choice_index') else None,
            "inventory": [item.name for item in self.player_character.inventory],
            "characters": [char.name for char in self.current_node.characters] if self.current_node else [],
            "items": [item.name for item in self.current_node.items] if self.current_node else [],
            "loot": [loot.name for loot in self.current_node.loot] if self.current_node else [],
            "story_arc": {
                "current_phase": self.story_arc.phases[self.story_arc.current_phase],
                "overall_story": self.story_arc.overall_story
            }
        }

    def _display_story_node(self):
        print("\n" + colored(self.current_node.title, 'yellow', attrs=['bold']))
        print(self.current_node.text)

        if self.current_node.characters:
            print(colored("\nCharacters:", 'cyan'))
            for character in self.current_node.characters:
                print(f"- {character.name}: {character.description}")

        if self.current_node.items:
            print(colored("\nItems:", 'green'))
            for item in self.current_node.items:
                print(f"- {item.name}: {item.description}")
                if item.effect:
                    print(f"Effect: {item.effect}")

        if self.current_node.loot:
            print(colored("\nLoot:", 'magenta'))
            for loot in self.current_node.loot:
                print(f"- {loot.name}: {loot.description}")

        print(colored("\nChoices:", 'yellow'))
        for i, choice in enumerate(self.current_node.choices, 1):
            print(f"{i}. {choice}")

    def _get_player_choice(self):
        while True:
            try:
                print("\nWhat do you want to do? (Enter the number of your choice)")
                choice = input("> ")
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(self.current_node.choices):
                    return choice_index
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def _handle_choice(self, choice_index):
        self.last_choice_index = choice_index
        choice = self.current_node.choices[choice_index]
        self.write_to_file("player_choice.txt", f"Player chose: {choice}")
        self._apply_choice_effects(choice)
        self._generate_story_node()
        self._display_story_node()

    def _apply_choice_effects(self, choice):
        effects_log = [f"Player chose: {choice}"]
        if self.current_node.loot:
            for loot in self.current_node.loot:
                self.player_character.inventory.append(loot)
                effects_log.append(f"Received: {loot.name}")
        if self.current_node.items:
            for item in self.current_node.items:
                self.player_character.equip_item(item)
                effects_log.append(f"Equipped: {item.name}")
                if item.effect:
                    effects_log.append(f"Effect: {item.effect}")
        self.write_to_file("choice_effects.txt", "\n".join(effects_log))

    def _load_game_state(self):
        game_state = SaveManager.load_game_state(self.game_id)
        if game_state:
            self.current_node = StoryNode.load_from_file(self.game_id, game_state["current_node_id"])
            self.player_character = Character.load_from_file(self.game_id, game_state["player_character_id"])
            if not self.current_node or not self.player_character:
                print("Error loading game state. Starting a new game.")
                self._new_game()
        else:
            print("Error loading game state. Starting a new game.")
            self._new_game()

    def _game_loop(self):
        while True:
            self._display_story_node()
            choice_index = self._get_player_choice()
            if choice_index is None:
                break
            self._handle_choice(choice_index)

if __name__ == "__main__":
    game = Game()
    game.start()
