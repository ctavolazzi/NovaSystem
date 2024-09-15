import json
import hashlib
import ollama
import os
import glob
from pyfiglet import Figlet
from termcolor import colored
from colorama import init
import logging

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
        self.character_id_counter = 0  # Add this line

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
            self._display_story_node()
        elif confirmation.lower() == "n":
            self._load_saved_game()
        else:
            print("Invalid choice. Please enter Y or N.")
            self._confirm_load_game()

    def _generate_story_node(self):
        context = self._build_context()
        story_node_data = self.ai_manager.generate_story_node(context)
        
        # Process characters and assign ids
        processed_characters = []
        for char_data in story_node_data.get("characters", []):
            char_id = self.generate_character_id()
            processed_characters.append(Character(char_id, char_data["name"], char_data["description"], {}))

        new_node = StoryNode(
            id=1,  # Or generate an appropriate ID
            title=story_node_data["title"],
            text=story_node_data["text"],
            choices=story_node_data["choices"],
            characters=processed_characters,
            items=[Item(item["name"], item["description"], item.get("effect", None)) for item in story_node_data.get("items", [])],
            loot=[Loot(loot["name"], loot["description"], loot.get("attributes", {})) for loot in story_node_data.get("loot", [])]
        )
        self.current_node = new_node
        if not self.story_tree:
            self.story_tree = StoryTree(TreeNode(new_node))
        else:
            self.story_tree.add_node(TreeNode(new_node))
        self.save_manager.save_game_state(self.game_id, self.current_node.id, self.player_character)

    def _build_context(self):
        return {
            "player_name": self.player_character.name,
            "player_class": self.player_character.attributes['class'],
            "current_situation": self.current_node.text if self.current_node else "Starting the adventure",
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
        self._get_player_choice()

    def _get_player_choice(self):
        while True:
            try:
                print("\nWhat do you want to do? (Enter the number of your choice)")
                choice = input("> ")
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(self.current_node.choices):
                    self._handle_choice(choice_index)
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def _handle_choice(self, choice_index):
        choice = self.current_node.choices[choice_index]
        self._apply_choice_effects(choice)
        self._generate_story_node()
        self._display_story_node()

    def _apply_choice_effects(self, choice):
        print(f"You chose: {choice}")
        if self.current_node.loot:
            for loot in self.current_node.loot:
                self.player_character.inventory.append(loot)
                print(f"You received: {loot.name}")
        if self.current_node.items:
            for item in self.current_node.items:
                self.player_character.equip_item(item)
                print(f"You equipped: {item.name}")
                if item.effect:
                    print(f"Effect: {item.effect}")

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
        self._display_story_node()
        while True:
            self._get_player_choice()

if __name__ == "__main__":
    game = Game()
    game.start()