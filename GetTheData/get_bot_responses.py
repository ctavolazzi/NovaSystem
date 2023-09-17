def get_bot_responses(bot1, bot2, prompt):
      # Begin with a user prompt or a default string
    nova_prime = bot1
    test_bot = bot2

    print(f"__________\n\n\n\n")
    nova_prime.respond_to(prompt)
    print(f"{bot1.name} says:\n\n\n\n")
    nova_prime_response = {"role": "assistant", "content": str(nova_prime.get_last_response().choices[0].message.content)}
    print(nova_prime_response["content"])
    print(f"\n\n\n\n__________")

    print(f"__________\n\n\n\n")
    test_bot.respond_to("Please ask Nova Prime a question. Ask it to help you design a never ending story called Buttknuckle Adventures, where the two main characters, Agarnigus Butt (Gus) and Claifornicus Knuckle (Cal) are space outlaws in the distant future who find a powerful magical scifi tech musical instrument called the Slaptok that they play, and the music accidentaly awakens aincient forces that want the instrument for themselves.")
    print(f"{bot2.name} says:\n\n\n\n")
    test_bot_response = {"role": "assistant", "content": str(test_bot.get_last_response().choices[0].message.content)}
    print(test_bot_response["content"])
    print(f"\n\n\n\n__________")

    return [nova_prime_response, test_bot_response]