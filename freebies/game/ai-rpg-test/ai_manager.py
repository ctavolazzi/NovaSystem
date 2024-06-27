import json
import ollama
import logging

class AIManager:
    def __init__(self, model="llama3"):
        self.model = model
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler("system_log.log")
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    def generate_content(self, content_description, context, json_example):
        prompt = f"Generate {content_description} for the story node based on the following context:\n{context}\n\nProvide the output in the following JSON format and include ONLY the JSON string in your response, without any additional text:\n{json_example}"
        
        self.logger.info(f"Generating {content_description}")
        self.logger.info(f"Prompt: {prompt}")
        
        print(f"Generating {content_description}...")
        
        try:
            response = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            content = response["message"]["content"]
            
            self.logger.info(f"Generated content: {content}")
            print(f"Generated content: {content}")
            
            # Parse and format the JSON response
            parsed_content = self._parse_json_response(content)
            
            self.logger.info(f"Parsed content: {parsed_content}")
            print(f"Parsed content: {parsed_content}")
            
            return parsed_content
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            error_message = f"Error generating {content_description}: {str(e)}"
            self.logger.error(error_message)
            print(error_message)
            return None

    def _parse_json_response(self, response):
        try:
            # Parse the response as JSON
            parsed_response = json.loads(response)
            
            # If the parsed response is not a dictionary, wrap it in one
            if not isinstance(parsed_response, dict):
                parsed_response = {"content": parsed_response}
            
            return parsed_response
        except json.JSONDecodeError as e:
            error_message = f"Error parsing JSON response: {str(e)}"
            self.logger.error(error_message)
            print(error_message)
            return {"choices": ["Continue"]}  # Provide a default choice to prevent the game from crashing

    def generate_title(self, context):
        json_example = '{"title": "<title>"}'
        return self.generate_content("a title", context, json_example)

    def generate_main_text(self, context):
        json_example = '{"text": "<main_text>"}'
        return self.generate_content("the main text", context, json_example)

    def generate_choices(self, context):
        json_example = '{"choices": ["<choice_1>", "<choice_2>", "<choice_3>"]}'
        prompt = f"Generate a list of choices for the player based on the following context:\n\nPlayer: {context['player_name']}\nClass: {context['player_class']}\nCurrent Situation: {context['current_situation']}\n\nProvide the output in the following JSON format and include ONLY the JSON string in your response, without any additional text:\n{json_example}"
        return self.generate_content("a list of choices for the player", prompt, json_example)

    def generate_characters(self, context):
        json_example = '{"characters": [{"name": "<name>", "description": "<description>"}, {"name": "<name>", "description": "<description>"}]}'
        prompt = f"Generate a list of characters for the story node based on the following context:\n\nPlayer: {context['player_name']}\nClass: {context['player_class']}\nCurrent Situation: {context['current_situation']}\n\nProvide the output in the following JSON format and include ONLY the JSON string in your response, without any additional text:\n{json_example}"
        return self.generate_content("a list of characters", prompt, json_example)

    def generate_items(self, context):
        json_example = '{"items": [{"id": "<id>", "name": "<name>", "description": "<description>", "effect": "<effect>"}, {"id": "<id>", "name": "<name>", "description": "<description>", "effect": "<effect>"}]}'
        prompt = f"Generate a list of items for the story node based on the following context:\n\nPlayer: {context['player_name']}\nClass: {context['player_class']}\nCurrent Situation: {context['current_situation']}\n\nProvide the output in the following JSON format and include ONLY the JSON string in your response, without any additional text:\n{json_example}"   
        return self.generate_content("a list of items", prompt, json_example)

    def generate_loot(self, context):
        json_example = '{"loot": [{"id": "<id>", "name": "<name>", "description": "<description>", "attributes": {"<attribute_key>": "<attribute_value>"}}, {"id": "<id>", "name": "<name>", "description": "<description>", "attributes": {"<attribute_key>": "<attribute_value>"}}]}'
        prompt = f"Generate a list of loot items for the story node based on the following context:\n\nPlayer: {context['player_name']}\nClass: {context['player_class']}\nCurrent Situation: {context['current_situation']}\n\nProvide the output in the following JSON format and include ONLY the JSON string in your response, without any additional text:\n{json_example}"
        return self.generate_content("a list of loot items", prompt, json_example)

    def generate_story_node(self):
        context = self._build_context()
        story_node_data = self.ai_manager.generate_story_node(context)
        
        if story_node_data is None:
            print("Error: Unable to generate story node. Using fallback node.")
            story_node_data = self._generate_fallback_node()

        new_node = StoryNode(
            id=1,  # Or generate an appropriate ID
            title=story_node_data.get("title", "Untitled Node"),
            text=story_node_data.get("text", "No text available."),
            choices=story_node_data.get("choices", ["Continue"]),
            characters=[Character(**char_data) for char_data in story_node_data.get("characters", [])],
            items=[Item(**item_data) for item_data in story_node_data.get("items", [])],
            loot=[Loot(**loot_data) for loot_data in story_node_data.get("loot", [])]
        )
        self.current_node = new_node
        if not self.story_tree:
            self.story_tree = StoryTree(TreeNode(new_node))
        else:
            self.story_tree.add_node(TreeNode(new_node))
        self.save_manager.save_game_state(self.game_id, self.current_node.id, self.player_character)

    def _generate_fallback_node(self):
        return {
            "title": "Unexpected Turn",
            "text": "The path ahead is unclear. What will you do?",
            "choices": ["Proceed carefully", "Find another way", "Rest and reconsider"],
            "characters": [],
            "items": [],
            "loot": []
        }
        
        return story_node_data