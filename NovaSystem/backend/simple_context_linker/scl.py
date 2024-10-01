class SimpleConceptLinker:
    def __init__(self):
        self.concepts = {}

    def add_concept(self, concept, link):
        self.concepts[concept.lower()] = link

    def remove_concept(self, concept):
        self.concepts.pop(concept.lower(), None)

    def link_concepts(self, text):
        words = text.split()
        for i, word in enumerate(words):
            lower_word = word.lower()
            if lower_word in self.concepts:
                words[i] = f'<a href="{self.concepts[lower_word]}">{word}</a>'
        return ' '.join(words)

    def run(self):
        print("Simple Concept Linker (type 'exit' to quit, 'add' to add a concept, 'remove' to remove a concept)")
        while True:
            user_input = input("Enter text: ").strip()
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'add':
                concept = input("Enter concept: ").strip()
                link = input("Enter link: ").strip()
                self.add_concept(concept, link)
                print(f"Added concept: {concept}")
            elif user_input.lower() == 'remove':
                concept = input("Enter concept to remove: ").strip()
                self.remove_concept(concept)
                print(f"Removed concept: {concept}")
            else:
                linked_text = self.link_concepts(user_input)
                print("Linked text:", linked_text)

if __name__ == "__main__":
    linker = SimpleConceptLinker()
    linker.add_concept("King Charles", "/concepts/king-charles")
    linker.add_concept("iPhone", "/concepts/iphone")
    linker.add_concept("NASA", "/concepts/nasa")
    linker.run()