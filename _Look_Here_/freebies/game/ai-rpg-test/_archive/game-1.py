import json
import hashlib
import ollama
import os
import glob
from pyfiglet import Figlet
from termcolor import colored
from colorama import init

from ai_manager import AIManager

# Initialize colorama
init(strip=not os.sys.stdout.isatty())

class TreeNode:
    def __init__(self, data):
        self.data = data
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)
        child.parent = None

    def get_level(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def print_tree(self):
        spaces = ' ' * self.get_level() * 3
        prefix = spaces + "|__" if self.parent else ""
        print(prefix + self.data.title)
        if self.children:
            for child in self.children:
                child.print_tree()

class StoryTree:
    def __init__(self, root):
        self.root = root

    def preorder_traversal(self, node):
        if node:
            print(node.data.title)
            for child in node.children:
                self.preorder_traversal(child)

    def postorder_traversal(self, node):
        if node:
            for child in node.children:
                self.postorder_traversal(child)
            print(node.data.title)

    def level_order_traversal(self):
        if not self.root:
            return
        queue = [self.root]
        while queue:
            node = queue.pop(0)
            print(node.data.title)
            queue.extend(node.children)

class StoryNode:
    def __init__(self, id, title, text, choices, characters, items, loot):
        self.id = id
        self.title = title
        self.text = text
        self.choices = choices
        self.characters = characters
        self.items = items
        self.loot = loot

    def save_to_file(self, game_id):
        data = {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "choices": self.choices,
            "characters": [char.__dict__ for char in self.characters],
            "items": [item.__dict__ for item in self.items],
            "loot": [loot.__dict__ for loot in self.loot]
        }
        os.makedirs(f"Games/game_{game_id}/nodes", exist_ok=True)
        with open(f"Games/game_{game_id}/nodes/node_{self.id}.json", "w") as file:
            json.dump(data, file)

    @staticmethod
    def load_from_file(game_id, node_id):
        file_path = f"Games/game_{game_id}/nodes/node_{node_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
                characters = [Character(**char) for char in data["characters"]]
                items = [Item(**item) for item in data["items"]]
                loot = [Loot(**loot) for loot in data["loot"]]
                return StoryNode(data["id"], data["title"], data["text"], data["choices"], characters, items, loot)
        return None

class StoryArc:
    def __init__(self):
        self.phases = ['introduction', 'rising_action', 'climax', 'resolution']
        self.current_phase = 0
        self.overall_story = self.generate_overall_story()
        self.key_elements = {}

    def generate_overall_story(self):
        context = {
            'phases': self.phases,
            'current_phase': self.phases[self.current_phase]
        }
        outline = ollama.chat(model='llama3', messages=[
            {"role": "user", "content": f"Generate a detailed story outline based on these phases: {json.dumps(context, indent=2)}"}
        ])
        return outline['message']['content']

    def update_phase(self):
        if self.current_phase < len(self.phases) - 1:
            self.current_phase += 1


class Character:
    def __init__(self, id, name, description, attributes, level=1, experience=0):
        self.id = id
        self.name = name
        self.description = description
        self.attributes = attributes
        self.level = level
        self.experience = experience
        self.skills = {}
        self.traits = {}
        self.inventory = []
        self.equipped_items = []

    def gain_experience(self, xp):
        self.experience += xp
        while self.experience >= self.xp_for_next_level():
            self.level_up()

    def xp_for_next_level(self):
        return 100 * self.level

    def level_up(self):
        self.level += 1
        self.experience -= self.xp_for_next_level()
        self.improve_attributes()
        self.unlock_new_skills()

    def improve_attributes(self):
        self.attributes['strength'] += 1  # Example attribute improvement

    def unlock_new_skills(self):
        pass

    def evolve_traits(self, choice):
        pass

    def equip_item(self, item):
        self.equipped_items.append(item)
        self.apply_item_effect(item)

    def apply_item_effect(self, item):
        for stat, value in item.effect.items():
            self.attributes[stat] += value

    def unequip_item(self, item):
        self.equipped_items.remove(item)
        self.remove_item_effect(item)

    def remove_item_effect(self, item):
        for stat, value in item.effect.items():
            self.attributes[stat] -= value

    def save_to_file(self, game_id):
        data = self.__dict__
        os.makedirs(f"Games/game_{game_id}/characters", exist_ok=True)
        with open(f"Games/game_{game_id}/characters/character_{self.id}.json", "w") as file:
            json.dump(data, file)

    @staticmethod
    def load_from_file(game_id, character_id):
        file_path = f"Games/game_{game_id}/characters/character_{character_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
                return Character(**data)
        return None

class Item:
    def __init__(self, id, name, description, effect):
        self.id = id
        self.name = name
        self.description = description
        self.effect = effect

class Loot:
    def __init__(self, id, name, description, attributes):
        self.id = id
        self.name = name
        self.description = description
        self.attributes = attributes

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
        existing_games = glob.glob("Games/game_*/")
        if not existing_games:
            return 1
        last_game_id = max(int(g.split("_")[1][:-1]) for g in existing_games)
        return last_game_id + 1

class Game:
    def __init__(self):
        self.ai_manager = AIManager()
        self.story_arc = StoryArc()
        self.player_character = None
        self.current_node = None
        self.story_tree = None
        self.game_id = None

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

        print("What is your character's name?")
        name = input("> ")
        character_id = 1  # Placeholder; implement proper ID generation
        self.player_character = Character(character_id, name, "The player character", {"class": self.starting_scenario})

        self.game_id = SaveManager.generate_game_id()
        os.makedirs(f"Games/game_{self.game_id}", exist_ok=True)
        self.player_character.save_to_file(self.game_id)
        self._generate_story_node()

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
                self.game_id = int(saved_games[choice_index].split("_")[1].split("/")[0])
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
        context_str = json.dumps(context, sort_keys=True)
        new_node = StoryNode(
            id=hashlib.md5(context_str.encode()).hexdigest(),
            title=story_node_data["title"],
            text=story_node_data["text"],
            choices=story_node_data["choices"],
            characters=story_node_data.get("characters", []),
            items=story_node_data.get("items", []),
            loot=story_node_data.get("loot", [])  # Ensure loot is included here
        )
        if self.current_node is None:
            self.current_node = TreeNode(new_node)
            self.story_tree = StoryTree(self.current_node)
        else:
            new_tree_node = TreeNode(new_node)
            self.current_node.add_child(new_tree_node)
            self.current_node = new_tree_node
        SaveManager.save_game_state(self.game_id, self.current_node.data.id, self.player_character)
        self._display_story_node()

    def _build_context(self):
        return {
            "player_name": self.player_character.name,
            "player_class": self.player_character.attributes['class'],
            "current_situation": self.current_node.data.text if self.current_node else "Starting the adventure",
            "story_arc": {
                "current_phase": self.story_arc.phases[self.story_arc.current_phase],
                "overall_story": self.story_arc.overall_story
            }
        }

    def _display_story_node(self):
        print("\n" + colored(self.current_node.data.title, 'yellow', attrs=['bold']))
        print(self.current_node.data.text)
        
        if self.current_node.data.characters:
            print(colored("\nCharacters:", 'cyan'))
            for character in self.current_node.data.characters:
                print(f"- {character}")
        
        if self.current_node.data.items:
            print(colored("\nItems:", 'green'))
            for item in self.current_node.data.items:
                print(f"- {item}")
        
        if self.current_node.data.loot:
            print(colored("\nLoot:", 'magenta'))
            for loot in self.current_node.data.loot:
                print(f"- {loot}")

        print(colored("\nChoices:", 'yellow'))
        for i, choice in enumerate(self.current_node.data.choices, 1):
            print(f"{i}. {choice}")
        self._get_player_choice()

    def _get_player_choice(self):
        while True:
            try:
                print("\nWhat do you want to do? (Enter the number of your choice)")
                choice = input("> ")
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(self.current_node.data.choices):
                    self._handle_choice(choice_index)
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def _handle_choice(self, choice_index):
        choice = self.current_node.data.choices[choice_index]
        # Here you would typically update game state based on the choice
        # For now, we'll just generate a new story node
        self._generate_story_node()

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