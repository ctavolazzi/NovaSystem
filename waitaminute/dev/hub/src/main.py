import os
import openai
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuration for different models
MODEL_CONFIG = {
    "text-davinci-003": {
        "model": "text-davinci-003",
        "max_tokens": 100,
        "temperature": 0.7
    },
    "gpt-3.5-turbo": {
        "model": "gpt-3.5-turbo",
        "messages": [],
        "max_tokens": 100,
        "temperature": 0.7
    }
}


class Router:
    def __init__(self):
        self.api_keys = {
            'openai': os.getenv('OPENAI_API_KEY')
        }

    def route(self, model_name, data):
        if model_name in MODEL_CONFIG:
            return self.openai_request(data)
        else:
            return f"Simulated response from {model_name} with data {data}"

    def openai_request(self, data):
        if 'davinci' in data['model'] or 'curie' in data['model'] or 'babbage' in data['model'] or 'ada' in data['model']:
            response = openai.Completion.create(
                model=data['model'],
                prompt=data['prompt'],
                max_tokens=data.get('max_tokens', 50),
                temperature=data.get('temperature', 0.7),
                top_p=data.get('top_p', 1.0),
                frequency_penalty=data.get('frequency_penalty', 0),
                presence_penalty=data.get('presence_penalty', 0)
            )
            return response.choices[0].text.strip()
        elif 'gpt-3.5-turbo' in data['model'] or 'gpt-4' in data['model']:
            response = openai.ChatCompletion.create(
                model=data['model'],
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": data['prompt']}],
                max_tokens=data.get('max_tokens', 50),
                temperature=data.get('temperature', 0.7),
                top_p=data.get('top_p', 1.0),
                frequency_penalty=data.get('frequency_penalty', 0),
                presence_penalty=data.get('presence_penalty', 0)
            )
            return response.choices[0].message.content.strip()
        else:
            raise ValueError(f"Unsupported model: {data['model']}")


class Model:
    def __init__(self, model_name, router, **kwargs):
        self.model_name = model_name
        self.router = router

        # Load the default configuration for the model
        self.default_params = MODEL_CONFIG.get(model_name, {})

        # Update default parameters with any passed kwargs
        self.default_params.update(kwargs)

    def make_request(self, prompt, **kwargs):
        # Update with custom parameters
        request_data = {
            "model": self.model_name,
            "prompt": prompt,
            **self.default_params,
            **kwargs
        }
        return self.router.route(self.model_name, request_data)


class Worker:
    def __init__(self, name, model):
        self.name = name
        self.model = model

    def execute(self, task):
        response = self.model.make_request(f"Execute task: {task}")
        return f"{self.name} worker result: {response}"


class WorkOrder:
    def __init__(self, user_request):
        self.user_request = user_request
        self.tasks = self.create_tasks(user_request)

    def create_tasks(self, request):
        # Example task creation logic
        return [
            f"Analyze investment opportunities in Microsoft based on {request}",
            f"Evaluate optimal portfolio allocation for maximum returns based on {request}"
        ]

    def get_tasks(self):
        return self.tasks


class Arbiter:
    def __init__(self, name, workers):
        self.name = name
        self.workers = workers

    def analyze(self, work_order):
        results = {worker.name: worker.execute(task) for worker, task in zip(self.workers, work_order.get_tasks())}
        combined_result = "\n".join(f"{name}: {result}" for name, result in results.items())
        return f"{self.name} arbiter result:\n{combined_result}"


class Magistrate:
    def __init__(self, arbiters):
        self.arbiters = arbiters

    def synthesize(self, work_order):
        results = {arbiter.name: arbiter.analyze(work_order) for arbiter in self.arbiters}
        combined_result = "\n".join(f"{name}: {result}" for name, result in results.items())
        return f"Magistrate synthesized decision:\n{combined_result}"


class RequestProcessor:
    def process_request(self, user_request):
        return WorkOrder(user_request)


class WorkerAssigner:
    def __init__(self, arbiters):
        self.arbiters = arbiters

    def assign_workers(self, work_order):
        # Example logic to assign workers to arbiters based on the tasks
        return self.arbiters


class Controller:
    def __init__(self, magistrate, request_processor, worker_assigner):
        self.magistrate = magistrate
        self.request_processor = request_processor
        self.worker_assigner = worker_assigner

    def execute_decision_process(self, user_request):
        work_order = self.request_processor.process_request(user_request)
        arbiters = self.worker_assigner.assign_workers(work_order)
        return self.magistrate.synthesize(work_order)


class Hub:
    def __init__(self, arbiter_configs, router):
        self.router = router
        self.workers = {name: Worker(name, Model(name, router, **config)) for name, config in arbiter_configs}
        self.arbiters = [
            Arbiter("Investment Analysis", [self.workers['Possibility'], self.workers['Permission']]),
            Arbiter("Portfolio Optimization", [self.workers['Preference']])
        ]
        self.magistrate = Magistrate(self.arbiters)
        self.request_processor = RequestProcessor()
        self.worker_assigner = WorkerAssigner(self.arbiters)
        self.controller = Controller(self.magistrate, self.request_processor, self.worker_assigner)

    def process(self, user_request):
        return self.controller.execute_decision_process(user_request)


# Example usage
if __name__ == "__main__":
    # Initialize the Router
    router = Router()

    # Worker (Arbiter) configurations (name, model parameters)
    arbiter_configs = [
        ("Possibility", {"model_name": "text-davinci-003", "temperature": 0.7, "max_tokens": 100}),
        ("Permission", {"model_name": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 100}),
        ("Preference", {"model_name": "text-davinci-003", "temperature": 0.5, "max_tokens": 50})
    ]

    # Create the Hub with the Arbiter configurations and Router
    tribunal_hub = Hub(arbiter_configs, router)

    # Process a query through the Hub
    result = tribunal_hub.process("How much of my portfolio should I invest in Microsoft for maximum returns?")
    print(result)