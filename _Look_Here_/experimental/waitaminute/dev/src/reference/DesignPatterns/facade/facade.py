class AIProcessingSubsystem:
    """
    A subsystem that might perform AI-related tasks.
    """
    def initialize(self) -> str:
        return "AIProcessingSubsystem: Initialized and ready to process."

    def process_data(self, data) -> str:
        return f"AIProcessingSubsystem: Processing data - {data}"

class DataAnalysisSubsystem:
    """
    A subsystem for data analysis.
    """
    def analyze(self, data) -> str:
        return f"DataAnalysisSubsystem: Analyzing data - {data}"

class NovaSystemFacade:
    """
    The Facade class provides a simple interface to the complex logic of NovaSystem's subsystems.
    """
    def __init__(self) -> None:
        self._ai_processor = AIProcessingSubsystem()
        self._data_analyzer = DataAnalysisSubsystem()

    def process_and_analyze_data(self, data) -> str:
        results = []
        results.append(self._ai_processor.initialize())
        results.append(self._ai_processor.process_data(data))
        results.append(self._data_analyzer.analyze(data))
        return "\n".join(results)

# Client Code
def client_code(facade: NovaSystemFacade) -> None:
    print(facade.process_and_analyze_data("Sample Data"), end="")

# Example usage
if __name__ == "__main__":
    facade = NovaSystemFacade()
    client_code(facade)
