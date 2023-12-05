from flyweight import FlyweightFactory, add_ai_component_to_system

def test_flyweight_pattern():
    # Creating a Flyweight Factory with some initial shared states
    factory = FlyweightFactory([
        ["NeuralNet", "Classifier", "Image"],
        ["NeuralNet", "Regressor", "TimeSeries"]
    ])

    # Listing initial flyweights
    print("Initial flyweights in the factory:")
    factory.list_flyweights()

    # Adding components and testing if flyweights are reused or newly created
    print("\nAdding a new AI component to the system:")
    add_ai_component_to_system(factory, ["NeuralNet", "Classifier", "Image", "DatasetX"])

    print("\nAdding another AI component to the system (should reuse flyweight):")
    add_ai_component_to_system(factory, ["NeuralNet", "Classifier", "Image", "DatasetY"])

    print("\nAdding a different AI component (should create new flyweight):")
    add_ai_component_to_system(factory, ["NeuralNet", "Classifier", "Audio", "DatasetZ"])

    # Listing final flyweights to verify the correct creation and reuse
    print("\nFinal flyweights in the factory:")
    factory.list_flyweights()

def main():
    test_flyweight_pattern()

if __name__ == "__main__":
    main()
