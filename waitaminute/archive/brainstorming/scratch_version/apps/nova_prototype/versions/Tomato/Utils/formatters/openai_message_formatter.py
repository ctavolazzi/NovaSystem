def openai_message_formatter(*args):
    valid_roles = ['user', 'assistant', 'system']
    formatted_messages = []

    # Function to format individual message
    def format_individual_message(message):
        # Check for dictionary input
        if isinstance(message, dict):
            if 'role' in message and 'content' in message:
                try:
                    role = str(message['role']) if not isinstance(message['role'], str) else message['role']
                    content = str(message['content']) if not isinstance(message['content'], str) else message['content']
                    return {'role': role, 'content': content}
                except Exception as e:
                    raise TypeError(f"Could not convert values to string. Error: {e}")
            else:
                raise ValueError("Invalid dictionary input: expected keys 'role' and 'content'")
        # Check for string input
        elif isinstance(message, str):
            return {'role': 'user', 'content': message}
        # Check for two string inputs
        elif len(message) == 2 and all(isinstance(arg, str) for arg in message):
            role, content = message if message[0].lower() in valid_roles else message[::-1]
            return {'role': role, 'content': content}
        # If input is a list, call openai_message_formatter recursively
        elif isinstance(message, list):
            return openai_message_formatter(*message)
        # If none of the conditions are met, raise a TypeError
        else:
            raise TypeError("Invalid input: expected either a single dictionary, a single string, or two strings")

    # Check if a list was passed
    if len(args) == 1 and isinstance(args[0], list):
        for item in args[0]:
            formatted_messages.append(format_individual_message(item))
    # If multiple arguments were passed
    elif len(args) > 1:
        for arg in args:
            formatted_messages.append(format_individual_message(arg))
    # If a single argument was passed
    else:
        formatted_messages.append(format_individual_message(args[0]))

    return formatted_messages
