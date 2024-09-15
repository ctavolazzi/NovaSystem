import json
import ollama

class StoryArc:
    def __init__(self):
        self.phases = ['introduction', 'rising_action', 'climax', 'resolution']
        self.current_phase = 0
        self.overall_story = self.generate_overall_story()
        self.key_elements = {}

    def generate_overall_story(self):
        context = {
            'phases': self.phases,
            'current_phase': self.phases[self.current_phase]
        }
        outline = ollama.chat(model='llama3', messages=[
            {"role": "user", "content": f"Generate a detailed story outline based on these phases: {json.dumps(context, indent=2)}"}
        ])
        return outline['message']['content']

    def update_phase(self):
        if self.current_phase < len(self.phases) - 1:
            self.current_phase += 1
