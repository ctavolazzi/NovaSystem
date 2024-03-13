from NovaHelper import stc
# from default_nova_config import default_nova_config


class NovaConfigManager:
    _DEFAULT_CONFIG = {
        "model": "gpt-3.5-turbo",
        "system_prompt": "You are a helpful assistant named Nova.",
        "api_key": None,
        "engine": "davinci",
        "temperature": 0.9,
        "max_tokens": 150,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.6,
        "stop": ["\n", " Human:", " Nova:"]
    }

    def __init__(self, config=None):
        self.parent = None
        if config:
            self.config = config
        else:
            self.config = self._DEFAULT_CONFIG

    def apply_config(self):
        # TODO: Implement this method.
        pass

    def test(self):
        stc(f'Testing ConfigManager...\n')
        # Verify that the default config is loaded and all attributes are as they should be.
        if self.parent:
          if self.parent.has_attribute('id'):
            stc(f'Parent: {self.parent.__class__.__name__}\n')
            stc(f'Parent ID: {self.parent.id}\n')
        else:
          stc(f'Parent: {self.parent}\n')
        if self.config:
            stc(f'Config found:\n\n')
            for key in self.config:
                stc(f'{key}: {self.config[key]}\n')
        else:
            stc('No config found.\n')
        stc("ConfigManager test complete.\n")

    def get_openai_api_key(self):
        if self.get_from_gonfig('openai_api_key'):
            return self.config['api_key']
        else:
            return None

    def get_from_config(self, key):
        if key in self.config:
            return self.config[key]
        else:
            return None

    def load_config(self, parent, config):
        self.parent = parent
        self.parent.config = config

    def add_config_attribute(self, key, value):
        self.config[key] = value

if __name__ == "__main__":
    nova_config_manager = NovaConfigManager(config={})
    nova_config_manager.test()