from abc import ABC, abstractmethod

# Builder Interface
class AIComponentBuilder(ABC):

    @property
    @abstractmethod
    def product(self):
        """Property to get the product."""
        pass

    @abstractmethod
    def add_ai_module(self):
        """Method to add an AI module to the product."""
        pass

    @abstractmethod
    def add_learning_capability(self):
        """Method to add learning capability to the product."""
        pass

    @abstractmethod
    def add_interaction_interface(self):
        """Method to add an interaction interface to the product."""
        pass

# Concrete Builder
class ConcreteAIComponentBuilder(AIComponentBuilder):
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset the builder to start with a fresh product."""
        self._product = AIComponent()

    @property
    def product(self):
        """Retrieve the built product and reset the builder."""
        product = self._product
        self.reset()
        return product

    def add_ai_module(self):
        """Add an AI module to the product."""
        self._product.add("AI Module")

    def add_learning_capability(self):
        """Add learning capability to the product."""
        self._product.add("Learning Capability")

    def add_interaction_interface(self):
        """Add an interaction interface to the product."""
        self._product.add("Interaction Interface")

# Product Class
class AIComponent:
    def __init__(self):
        self.parts = []

    def add(self, part):
        """Add a part to the component."""
        self.parts.append(part)

    def list_parts(self):
        """List all parts of the component."""
        print(f"AI Component Parts: {', '.join(self.parts)}", end="")

# Director Class
class Director:
    def __init__(self):
        self._builder = None

    @property
    def builder(self):
        """Property to get and set the builder."""
        return self._builder

    @builder.setter
    def builder(self, builder):
        self._builder = builder

    def build_minimal_ai_component(self):
        """Build a minimal AI component."""
        self.builder.add_ai_module()

    def build_full_featured_ai_component(self):
        """Build a full-featured AI component."""
        self.builder.add_ai_module()
        self.builder.add_learning_capability()
        self.builder.add_interaction_interface()

# Client Code (optional here, might be in a separate test file)
if __name__ == "__main__":
    director = Director()
    builder = ConcreteAIComponentBuilder()
    director.builder = builder

    print("Building a minimal AI component:")
    director.build_minimal_ai_component()
    builder.product.list_parts()

    print("\n\nBuilding a full-featured AI component:")
    director.build_full_featured_ai_component()
    builder.product.list_parts()

    print("\n\nBuilding a custom AI component:")
    builder.add_ai_module()
    builder.add_interaction_interface()
    builder.product.list_parts()
