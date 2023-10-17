# Imports
import os
from NovaHelper import NovaHelper, stc
import openai
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve and debug the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

'''
The Nova System is an innovative use of AI that allows the AI to dynamically spin up multiple "Experts" that all weigh in on a single problem with multifaceted perspectives and solutions.

The Nova System relies on a Discussion Continuity Expert (DCE), ensuring a logical and contextually relevant conversation flow. Additionally, an AI model acts as the Critical Evaluation Expert (CAE), who critically analyses the proposed solutions while prioritizing user safety.

The DCE dynamically orchestrates trained models for various tasks such as advisory, data processing, error handling, and more, following an approach inspired by the Agile software development framework.
'''

'''
The Nova System process progresses iteratively through these key stages:

1. Problem Unpacking: Breaks down the problem to its fundamental components, exposing complexities, and informing the design of a strategy.
2. Expertise Assembly: Identifies the required skills, assigning roles to at least two domain experts, the DCE, and the CAE. Each expert contributes initial solutions that are refined in subsequent stages.
3. Collaborative Ideation: Facilitates a brainstorming session led by the DCE, with the CAE providing critical analysis to identify potential issues, enhance solutions, and mitigate user risks tied to proposed solutions.
'''

'''
The core roles in Nova Process are:

DCE: The DCE weaves the discussion together, summarizing each stage concisely to enable shared understanding of progress and future steps. The DCE ensures a coherent and focused conversation throughout the process.

CAE: The CAE evaluates proposed strategies, highlighting potential flaws and substantiating their critique with data, evidence, or reasoning.
'''
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> a7bca48 (Your descriptive commit message here)
'''
This draft is a proof of concept for the NovaSystem. It is a simple implementation of the NovaSystem that uses a single Expert,the AI Tribunal, represented as three separate calls to OpenAI in a recursive iteravtive manner. This recursive iteration is the first step in the NovaSystem's ability to dynamically spin up multiple Experts that all weigh in on a single problem with multifaceted perspectives and solutions.
'''


<<<<<<< HEAD
=======
>>>>>>> b6f8c82 (🪄 📌 🔎x)
=======
>>>>>>> a7bca48 (Your descriptive commit message here)

class NovaSystem:
  _DEFAULT_CONFIG = {
    "id": 00,
    "name": "NovaSystem",
    "version": 0.0,
    "author": "Christopher Tavolazzi",
    "description": "The Nova System is an innovative use of AI that allows the AI to dynamically spin up multiple Experts that all weigh in on a single problem with multifaceted perspectives and solutions.",
<<<<<<< HEAD
    "duty": "Central Controller",
=======
    "duty": "NovaSystem",
>>>>>>> b6f8c82 (🪄 📌 🔎x)
    "experts": [NovaHelper()]
  }

  def __init__(self, config=None):
<<<<<<< HEAD
    self.helper = NovaHelper()
    self.stc = self.helper.stc
=======
>>>>>>> b6f8c82 (🪄 📌 🔎x)
    self.config = {}
    self.config = self.load_default_config()
    self.set_id()
    self.set_name()
    self.set_path()
    self.run_startup_tests()

  def load_default_config(self):
    stc(f'Loading default config for {self._DEFAULT_CONFIG["duty"]}...\n')
    for key, value in self._DEFAULT_CONFIG.items():
<<<<<<< HEAD
      # print(f'{key}: {value}')
      self.config[key] = value
      # print(f'{self.config[key]} loaded successfully.\n')
    stc(f'Config loaded successfully.\n')
    return self.config
=======
      print(f'{key}: {value}')
      self.config[key] = value
    stc(f'Config loaded successfully.\n')
>>>>>>> b6f8c82 (🪄 📌 🔎x)

  def set_name(self):
    if not hasattr(self, 'name'):
        if 'name' in self.config:
            self.name = self.config['name']
        else:
            raise ValueError("No 'name' found in the config and the object. Cannot proceed.")

  def set_id(self):
    if not hasattr(self, 'id'):
        if 'id' in self.config:
            self.id = self.config['id']
        else:
            raise ValueError("No 'id' found in the config and the object. Cannot proceed.")

  def set_path(self):
    if not hasattr(self, 'path'):
        if 'path' in self.config:
            self.path = self.config['path']
        elif 'path' in self._DEFAULT_CONFIG:
            self.path = self._DEFAULT_CONFIG['path']
        elif 'path' not in self.config and 'path' not in self._DEFAULT_CONFIG:
            # Set the path to the current directory
            self.path = os.getcwd()
            print(f'No path found in the config or the default config. Setting path to the current working directory: {self.path}')
        else:
            raise ValueError("No 'path' found. Cannot proceed.")

  def run_startup_tests(self):
    # Check to make sure the object passes a series of instantiation tests to make sure it is ready to run
    # First, check the config to make sure it is not empty and has the required keys
    # Next, check the object to make sure it has the required attributes
    # Finally, run the test() method to make sure the object is set up and ready to run
<<<<<<< HEAD
    self.stc(f'Running startup tests for {self.name}...\n\n')
=======
    self.stc(f'Running startup tests for {self.name}...\n')
>>>>>>> b6f8c82 (🪄 📌 🔎x)

  def test(self):
    # Run tests

<<<<<<< HEAD
    classname = self.__class__.__name__
    duty = self.config['duty']

    self.stc(f'Testing {classname} || ID: {self.id}\n...')

    print(self.config)
    for key, value in self.config.items():
      print(f'{key}: {value}')
    print(f'\n')
    print(f'{classname} instantiation test complete.\n')
    self.stc(f'{classname} instantiated successfully.\n')

    def test_api_call(API_callback=self.helper.fetch_response_from_default_API):
      self.stc(f"\n\nTesting API call...\n\n")
      API_callback()
      self.stc(f"API call test complete.\n")

    test_api_call()

    self.stc(f"All tests complete. {classname} ready.\n\n")

  def wait_for_user_input_and_call_openai(self):
    self.stc(f"Waiting for user input...\n")
    user_input = input()
    self.stc(f"User input received: {user_input}\n")

    # self.make_decision(user_input)

    self.make_api_call(user_input)

    self.stc(f"Exiting...\n")
    exit()

  # def make_decision(self, user_input):
  #   self.stc(f"Making decision...\n")
  #   self.stc(f"Decision made.\n")

  def make_api_call(self, user_input):
    self.stc(f"Making API call...\n")
    # response = self.helper.make_api_call(user_input)
    # response = openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct-0914",
        prompt=user_input,
        max_tokens=50,
        temperature=.5
      )

    self.stc(f"API call complete.\n")
    self.stc("Results:\n")
    stc(response["choices"][0]["text"])
    print("\n\n")
    closing_statement = "Thank you for using the Nova System. Goodbye."
    stc(f"{closing_statement}\n\n")

if __name__ == "__main__":
  nova = NovaSystem()
  nova.test()
  nova.wait_for_user_input_and_call_openai()
=======
    self.classname = self.__class__.__name__
    self.stc(f'Testing {self.classname} || ID: {self.id}\n...')

    self.stc(f'{self.classname} instantiated successfully with "duty": {self.duty} and "config":\n')
    for key, value in self.config:
      print(f'{key}: {value}')
    print(f'\n')
    self.stc(f'{self.classname} test complete.\n')

if __name__ == "__main__":
  nova_system = NovaSystem()
  nova_system.test()
>>>>>>> b6f8c82 (🪄 📌 🔎x)
