# story_tree.py

import json
import os
from utils import ensure_game_directory
from story_node import StoryNode
import uuid

class TreeNode:
    def __init__(self, data):
        self.id = str(uuid.uuid4())  # Generate a unique ID for the TreeNode
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

    def to_dict(self):
        return {
            "id": self.id,
            "data": self.data.to_dict(),
            "children": [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data_dict):
        node_data = StoryNode(**data_dict["data"])
        node = cls(node_data)
        node.id = data_dict["id"]
        for child_dict in data_dict["children"]:
            child = cls.from_dict(child_dict)
            node.add_child(child)
        return node

class StoryTree:
    def __init__(self, root):
        self.root = root
        self.nodes = {root.id: root}

    def add_node(self, node, parent_id=None):
        if parent_id is None:
            parent_id = self.root.id
        parent_node = self.nodes.get(parent_id)
        if parent_node:
            parent_node.children.append(node)
            self.nodes[node.id] = node

    def to_dict(self):
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        }

    def generate_new_node_id(self):
        return str(uuid.uuid4())

    def find_node(self, node_id, current_node=None):
        if current_node is None:
            current_node = self.root

        if current_node.id == node_id:
            return current_node

        for child in current_node.children:
            result = self.find_node(node_id, child)
            if result is not None:
                return result

        return None

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

    def print_tree(self):
        self.root.print_tree()

    def save_tree(self, game_id):
        game_dir = ensure_game_directory(game_id)
        file_path = os.path.join(game_dir, "story_tree.json")
        tree_data = self.root.to_dict()
        with open(file_path, 'w') as f:
            json.dump(tree_data, f, indent=2)

    @classmethod
    def load_tree(cls, game_id):
        game_dir = ensure_game_directory(game_id)
        file_path = os.path.join(game_dir, "story_tree.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                tree_data = json.load(f)
            root_node = TreeNode.from_dict(tree_data)
            return cls(root_node)
        return None

class StoryNode:
    def __init__(self, id, title, text, choices, characters, items, loot):
        self.id = id
        self.title = title
        self.text = text
        self.choices = choices
        self.characters = characters
        self.items = items
        self.loot = loot

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "choices": self.choices,
            "characters": [char.to_dict() for char in self.characters],
            "items": [item.to_dict() for item in self.items],
            "loot": [loot.to_dict() for loot in self.loot]
        }