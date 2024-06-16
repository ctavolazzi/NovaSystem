class Hub:
    def __init__(self, config):
        self.router = config["router"]
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