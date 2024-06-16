import sys
sys.path.append("..")

import gradio as gr
from abc import ABC, abstractmethod
from bots.Bot import Bot


class TestBot(Bot):
    def __init__(self, config):
        super().__init__(config)

    def execute(self, input_text):
        self.log(f"Received input: {input_text}")
        # Add your custom bot logic here
        output_text = f"TestBot processed input: {input_text}"
        return output_text

def create_bot():
    bot_config = {
        'name': 'TestBot',
        'model': 'default_model',
        'log_level': 'INFO'
    }
    return TestBot(bot_config)

def main():
    bot = create_bot()

    def bot_interface(input_text):
        output_text = bot.execute(input_text)
        return output_text

    def test_say_name():
        output_text = bot.say_name()
        return output_text

    def test_generate_random_phrase():
        output_text = bot.generate_random_phrase()
        return output_text

    with gr.Blocks(title="TestBot Interface") as iface:
        gr.Markdown("Interact with the TestBot using Gradio interface.")

        with gr.Row():
            input_textbox = gr.Textbox(label="Enter your message")
            output_textbox = gr.Textbox(label="Bot Response")

        with gr.Row():
            test_name_btn = gr.Button("Test Say Name")
            test_name_output = gr.Textbox(label="Test Say Name Output")

        with gr.Row():
            test_phrase_btn = gr.Button("Test Generate Random Phrase")
            test_phrase_output = gr.Textbox(label="Test Generate Random Phrase Output")

        input_textbox.submit(bot_interface, inputs=input_textbox, outputs=output_textbox)
        test_name_btn.click(test_say_name, outputs=test_name_output)
        test_phrase_btn.click(test_generate_random_phrase, outputs=test_phrase_output)

    iface.launch()

if __name__ == "__main__":
    main()