from nova_prompt import return_nova_prompt
from bot import Bot
from get_bot_responses import get_bot_responses

# Automatically run the Nova prompt and save the output to a markdown file
def run_nova_prompt():
    print("Running Nova Prompt...")
    n_p = return_nova_prompt()

    # Instantiate the bots
    nova_prime = Bot(system_message=n_p)
    nova_prime.set_name("Nova Prime")
    nova_prime.identify()

    test_bot = Bot("You are a helpful bot that is curious about the world. You like asking questions and your name is Botticus.")
    test_bot.set_name("Test Bot")
    test_bot.identify()

    starter_prompt = "Hello. You are about to participate in a test where you will be speaking to another bot. Please introduce yourself now."
    test_bot.respond_to(starter_prompt)
    nova_prime.respond_to(starter_prompt)
    print(f"__________\n\n\n\n")
    print(f"{test_bot.name} responds to starter prompt:\n\n\n\n")
    print(test_bot.get_last_response().choices[0].message.content)
    print(f"{nova_prime.name} responds to starter prompt:\n\n\n\n")
    print(nova_prime.get_last_response().choices[0].message.content)

    conversation_length = 5  # Modify this value to set the desired conversation length
    count = 0

    # Have an iterative conversation between the bots
    # Have one bot ask a question, and the other bot respond, and the first bot wait for the response and then ask another question

    current_message = starter_prompt
    for _ in range(conversation_length):
        print(f"__________\n\n\n\nConversation Iteration {count}\n\n\n\n__________")
        nova_prime.respond_to(test_bot.get_last_response().choices[0].message.content)
        nova_response_text = nova_prime.get_last_response().choices[0].message.content
        print(f"{nova_prime.name} says:\n\n\n\n")
        print(nova_response_text)
        print(f"\n\n\n\n__________")
        test_bot.respond_to(nova_response_text)
        test_bot_response_text = test_bot.get_last_response().choices[0].message.content
        print(f"{test_bot.name} says:\n\n\n\n")
        print(test_bot_response_text)
        print(f"\n\n\n\n__________")
        count += 1

    # Uncomment the line below if you want to print the last message
    # print(f"Last Message: {current_message}")


def run():
    run_nova_prompt()

if __name__ == "__main__":
    run()
