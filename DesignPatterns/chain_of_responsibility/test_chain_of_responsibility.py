from chain_of_responsibility import AIModelHandler, DataPreprocessingHandler, VisualizationHandler, AbstractHandler

def test_individual_handler(handler: AbstractHandler, request: str):
    result = handler.handle(request)
    if result:
        print(f"  Handled by {handler.__class__.__name__}: {result}")
    else:
        print(f"  {handler.__class__.__name__} passed the request.")

def test_full_chain(chain_head: AbstractHandler, request: str):
    print(f"\nTesting full chain with request: {request}")
    result = chain_head.handle(request)
    if result:
        print(f"Handled by chain: {result}")
    else:
        print("Request was left unhandled by the full chain.")

def main():
    # Setting up individual handlers
    ai_model_handler = AIModelHandler()
    data_handler = DataPreprocessingHandler()
    visualization_handler = VisualizationHandler()

    # Building the chain
    ai_model_handler.set_next(data_handler).set_next(visualization_handler)

    # Testing individual handlers
    test_requests = ["Train", "Preprocess", "Visualize", "Deploy", "Unknown"]
    for request in test_requests:
        print(f"\nTesting AIModelHandler with request: {request}")
        test_individual_handler(ai_model_handler, request)
        print(f"\nTesting DataPreprocessingHandler with request: {request}")
        test_individual_handler(data_handler, request)
        print(f"\nTesting VisualizationHandler with request: {request}")
        test_individual_handler(visualization_handler, request)

    # Testing the full chain
    for request in test_requests:
        test_full_chain(ai_model_handler, request)

if __name__ == "__main__":
    main()
