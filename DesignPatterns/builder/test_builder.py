from builder import Director, ConcreteAIComponentBuilder

def test_minimal_ai_component(director, builder):
    print("Testing minimal AI component construction:")
    director.builder = builder
    director.build_minimal_ai_component()
    builder.product.list_parts()

def test_full_featured_ai_component(director, builder):
    print("\nTesting full-featured AI component construction:")
    director.builder = builder
    director.build_full_featured_ai_component()
    builder.product.list_parts()

def test_custom_ai_component(builder):
    print("\nTesting custom AI component construction:")
    builder.add_ai_module()
    builder.add_learning_capability()  # Adding only specific parts
    builder.product.list_parts()

def main():
    director = Director()
    builder = ConcreteAIComponentBuilder()

    test_minimal_ai_component(director, builder)
    test_full_featured_ai_component(director, builder)
    test_custom_ai_component(builder)

if __name__ == "__main__":
    main()
