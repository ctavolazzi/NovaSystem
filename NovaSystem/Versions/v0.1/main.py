print("Welcome to the NovaSystem")

import asyncio
from termcolor import colored

async def delayed_print(text, delay=0.1, color=None, attrs=[]):
    for char in text:
        if color:
            print(colored(char, color, attrs=attrs), end='', flush=True)
        else:
            print(char, end='', flush=True)
        await asyncio.sleep(delay)
    print()  # Newline at the end

async def message_queue(messages):
    for message in messages:
        text, kwargs = message.get('text', ''), message.get('kwargs', {})
        await delayed_print(text, **kwargs)

# Example usage
async def main():
    messages = [
        {'text': 'Hello, ', 'kwargs': {'delay': 0.01, 'color': 'red'}},
        {'text': 'World!', 'kwargs': {'delay': 0.01, 'color': 'green', 'attrs': ['bold']}},
        {'text': 'How are you?', 'kwargs': {'delay': 0.01, 'color': 'blue'}}
    ]
    await message_queue(messages)

if __name__ == '__main__':
    asyncio.run(main())

# We need to engineer a system where this is a call to OpenAI ChatCompletion API
# It needs to be aware of what color the words are, and capale of setting the speed with which they render