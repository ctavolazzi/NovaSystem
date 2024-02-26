import os
from Modules.Helpers.NovaHelper import NovaHelper
from Modules.Tribunal.NovaTribunal import NovaTribunal

class NovaSystem:
    _DEFAULT_CONFIG = {
        "id": 00,
        "name": "NovaSystem",
        "version": 0.0,
        "author": "Christopher Tavolazzi",
        "description": "The Nova System is an innovative use of AI that allows the AI to dynamically spin up multiple Experts that all weigh in on a single problem with multifaceted perspectives and solutions.",
        "duty": "NovaSystem",
        "experts": [NovaHelper(), NovaTribunal()]
    }

    def __init__(self, config=None):
        self.config = {}
        self.config = self.load_default_config()
        self.set_id()
        self.set_name()
        self.set_path()
        self.run_startup_tests()
    
    def load_default_config(self):
        stc(f'Loading default config for {self._DEFAULT_CONFIG["duty"]}...\n')
        for key, value in self._DEFAULT_CONFIG.items():
            print(f'{key}: {value}')
        self.config[key] = value
        stc(f'Config loaded successfully.\n')

    def set_name(self):
        if not hasattr(self, 'name'):
            if 'name' in self.config:
                self.name = self.config['name']

class NovaTribunal:
    _DEFAULT_CONFIG = {
        "id": 00,
        "name": "NovaSystem",
        "version": 0.0,
        "author": "Christopher Tavolazzi",
        "description": "The Nova System is an innovative use of AI that allows the AI to dynamically spin up multiple Experts that all weigh in on a single problem with multifaceted perspectives and solutions.",
        "duty": "NovaSystem",
        "experts": [NovaHelper(), NovaTribunal()]
    }

    def __init__(self):
        pass
    
    def evaluate(self, proposed_solution):
        # Evaluate the proposed solution
        print('Evaluating proposed solution...')
        return 'Accepted'

    def provide_critical_analysis(self, proposed_solution):
        # Provide critical analysis of the proposed solution
        print('Providing critical analysis of proposed solution...')
        return 'Critical analysis provided.'


import os
from Nova import NovaSystem
from Nova import NovaTests

def main():
    print("NovaSystem Initializing...")
    print("Rest of program unimplemented.")