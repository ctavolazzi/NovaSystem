# environment for testing AI behaviors in the MIBA environment

import requests

class Arena:
    def __init__(self):
        self.subscribers = []
        self.ais = []

    def add_subscriber(self, subscriber):
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)

    def receive_api_request(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

            if 'ai_models' in response.json():
                self.ai_models = response.json()['ai_models']
                self.notify_subscribers()
            else:
                print("Error: The response does not contain 'ai_models'")
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except requests.exceptions.ConnectionError as conn_err:
            print(f'Error connecting: {conn_err}')
        except requests.exceptions.Timeout as timeout_err:
            print(f'Timeout error: {timeout_err}')
        except requests.exceptions.RequestException as req_err:
            print(f'An error occurred: {req_err}')

    def notify_subscribers(self):
        for subscriber in self.subscribers:
            if hasattr(subscriber, 'update'):
                subscriber.update(self.ai_models)
            else:
                print(f"Error: Subscriber {subscriber} does not have an update method")

    def add_data(self, key, value):
        self.data[key] = value

# Create an instance of the Arena class
arena = Arena()

# Define the Base Arbiter Class
class BaseArbiter:
    def ask_question(self, question):
        return input(question)

# Define Subclasses for Each Area of Concern
class Arbiter_of_Possibility(BaseArbiter):
    def process(self, user_response):
        # API call logic specific to "Is it possible?"
        arena.add_data("possibility", user_response)

class Arbiter_of_Permission(BaseArbiter):
    def process(self, user_response):
        # API call logic specific to "Is it permitted?"
        arena.add_data("permission", user_response)

class Arbiter_of_Preference(BaseArbiter):
    def process(self, user_response):
        # API call logic specific to "Is it preferred?"
        arena.add_data("preference", user_response)

# Define the NovaTribunal Class
# Corrected NovaTribunal Class Initialization
class NovaTribunal:
    def __init__(self, arbiter1=None, arbiter2=None, arbiter3=None):
        self.arbiters = [arbiter1, arbiter2, arbiter3]
        if all(arbiter is None for arbiter in self.arbiters):
            self.arbiters = [Arbiter_of_Possibility(), Arbiter_of_Permission(), Arbiter_of_Preference()]

    def execute_tribunal(self):
        user_responses = []
        for arbiter in self.arbiters:
            question = "Please enter your query: "
            user_response = arbiter.ask_question(question)
            user_responses.append(user_response)
            # Chained API call logic here
            arbiter.process(user_response)

if __name__ == "__main__":
    tribunal = NovaTribunal()
    tribunal.execute_tribunal()