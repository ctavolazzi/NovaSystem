class Controller:
    def __init__(self, config):
        self.magistrate = config["magistrate"]
        self.request_processor = config["request_processor"]
        self.worker_assigner = config["worker_assigner"]

    def execute_decision_process(self, user_request):
        work_order = self.request_processor.process_request(user_request)
        arbiters = self.worker_assigner.assign_workers(work_order)
        return self.magistrate.synthesize(work_order)