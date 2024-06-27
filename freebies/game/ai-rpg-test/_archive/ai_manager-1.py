import uuid
import json
import hashlib
import ollama
from cache_manager import CacheManager
import re
from item import Item
from loot import Loot

class AIManager:
    def __init__(self, model="llama3"):
        self.model = model
        self.cache_manager = CacheManager()

    def generate_story_node(self, context):
        context_hash = self._hash_context(context)
        cached_result = self.cache_manager.get(context_hash)
        if cached_result:
            return cached_result

        prompt = self._build_prompt(context)
        try:
            response = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            print("Raw response from Ollama API:", response)  # Print the raw response
            story_node_data = self._parse_response(response["message"]["content"])
            self.cache_manager.set(context_hash, story_node_data)
            return story_node_data
        except Exception as e:
            print(f"Error in AI response: {e}")
            return self._generate_fallback_node()

    def _hash_context(self, context):
        context_str = json.dumps(context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()

    def _build_prompt(self, context):
        return f"""
        Generate a story node based on:
        Player: {context['player_name']} ({context['player_class']})
        Current situation: {context['current_situation']}
        Story phase: {context['story_arc']['current_phase']}
        Overall story: {context['story_arc']['overall_story']}
        
        The response should be in the following JSON format:
        {{
            "title": "Title of the story node",
            "text": "Main text describing the situation including {context['player_name']}.",
            "choices": ["Choice 1", "Choice 2", "Choice 3"],
            "characters": [
                {{"name": "{context['player_name']}", "description": "Description of the main player character."}},
                {{"name": "Character 2", "description": "Description of Character 2"}}
            ],
            "items": [
                {{"name": "Item 1", "description": "Description of Item 1", "effect": null}},
                {{"name": "Item 2", "description": "Description of Item 2", "effect": null}}
            ],
            "loot": [
                {{"name": "Loot 1", "description": "Description of Loot 1", "attributes": {{}}}},
                {{"name": "Loot 2", "description": "Description of Loot 2", "attributes": {{}}}}
            ]
        }}
        Ensure the story node aligns with the current story phase and overall story arc.
        """

    def _parse_response(self, response_text):
        try:
            data = self._response_adapter(response_text)
            return {
                "title": data["title"],
                "text": data["text"],
                "choices": data["choices"],
                "characters": [self._create_character(char) for char in data.get("characters", [])],
                "items": [self._create_item(item) for item in data.get("items", [])],
                "loot": [self._create_loot(loot) for loot in data.get("loot", [])]
            }
        except Exception as e:
            print("Error parsing AI response:", e)  # Print the parsing error
            return self._generate_fallback_node()

    def _response_adapter(self, response_text):
        try:
            # Use regex to find the JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in the response")

            json_str = json_match.group()
            
            # Remove any control characters
            json_str = ''.join(char for char in json_str if ord(char) >= 32)
            
            data = json.loads(json_str)

            # Ensure all required fields are present
            required_fields = ["title", "text", "choices", "characters", "items", "loot"]
            for field in required_fields:
                if field not in data:
                    data[field] = [] if field in ["choices", "characters", "items", "loot"] else ""

            return data
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error extracting JSON from response: {e}")
            print(f"Raw response: {response_text}")
            raise

    def _create_character(self, char_data):
        return {"name": char_data.get("name", "Unknown"), "description": char_data.get("description", "")}

    def _create_item(self, item_data):
        return Item(
            id=item_data.get("id", uuid()),
            name=item_data.get("name", "Unknown"),
            description=item_data.get("description", ""),
            effect=item_data.get("effect", {})
        )

    def _create_loot(self, loot_data):
        return Loot(
            id=loot_data.get("id", uuid()),
            name=loot_data.get("name", "Unknown"),
            description=loot_data.get("description", ""),
            attributes=loot_data.get("attributes", {})
        )

    def _generate_fallback_node(self):
        return {
            "title": "Unexpected Turn",
            "text": "The path ahead is unclear. What will you do?",
            "choices": ["Proceed carefully", "Find another way", "Rest and reconsider"],
            "characters": [],
            "items": [],
            "loot": []
        }
