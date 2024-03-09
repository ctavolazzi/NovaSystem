# src/AI/AIForum/aiforum.py

import random
import logging

# Setting up basic logging
logging.basicConfig(level=logging.INFO)

class User:
    """
    Represents a user in the forum.

    Attributes:
        username (str): The username of the user.
        messages (list): A list of messages posted by the user.
    """

    def __init__(self, username):
        self.username = username
        self.messages = []

    def post_message(self, forum, message):
        """
        Post a message to the forum.

        Args:
            forum (Forum): The forum to post the message to.
            message (str): The message to post.
        """
        try:
            if not message:
                raise ValueError("Message cannot be empty")
            forum.receive_message(self, message)
            self.messages.append(message)
        except Exception as e:
            logging.error(f"Error in post_message: {e}")

class AIUser(User):
    """
    Represents an AI user in the forum.
    Inherits from User.
    """
    def __init__(self, username, ai_model):
        super().__init__(username)
        self.ai_model = ai_model
        self.conversation_history = []

    responses = ["Hello there!", "How's it going?", "Interesting conversation!"]


    def generate_response(self, input_text):
        """
        Generates a response using the AI model based on the given input text.

        Args:
            input_text (str): The input text to generate a response for.

        Returns:
            str: The AI-generated response.
        """
        # Depending on the AI model's interface, you might need to tokenize the input
        # or prepare it in a specific format. For example, if using HuggingFace models:
        # Tokenize and generate text using HuggingFaceGuy
        model_inputs = self.ai_model.tokenize_inputs([input_text])
        generated_text = self.ai_model.generate_text(model_inputs)
        return generated_text.strip()

    def respond(self, forum):
        # Get the last message from the forum
        if forum.messages:
            last_message = forum.messages[-1][1]  # Assuming this is the message text
        else:
            last_message = "Starting conversation"

        # Generate response based on the last message
        response = self.generate_response(last_message)
        self.post_message(forum, response)

class Forum:
    """
    Represents the forum where users and AI bots can post messages.

    Attributes:
        messages (list): A list of messages in the forum.
    """

    def __init__(self):
        self.messages = []

    def receive_message(self, user, message):
        """
        Receive a message from a user and trigger an AI response.

        Args:
            user (User): The user who is posting the message.
            message (str): The message being posted.
        """
        self.messages.append((user.username, message))
        logging.info(f"{user.username} says: {message}")
        self.trigger_ai_response()

    def trigger_ai_response(self):
        """
        Trigger an AI response to the latest message.
        """
        ai_user = AIUser("AI_Bot")
        ai_user.respond(self)

# Test functions for the forum
def test_forum():
    """
    Test function for the Forum class.
    """
    forum = Forum()
    alice = User("Alice")
    bob = User("Bob")

    alice.post_message(forum, "Hi, everyone!")
    bob.post_message(forum, "")
    assert len(forum.messages) == 1  # Expecting only Alice's message due to error handling

class AIForum:
    """
    Represents the controller or manager for the AI Forum.

    Attributes:
        forum (Forum): The forum instance that the AIForum manages.
    """

    def __init__(self):
        self.forum = Forum()

    def add_user_message(self, username, message):
        """
        Adds a message from a user to the forum.

        Args:
            username (str): The username of the user posting the message.
            message (str): The content of the message.
        """
        user = User(username)
        user.post_message(self.forum, message)

    def display_forum_messages(self):
        """
        Displays all messages in the forum.
        """
        for username, message in self.forum.messages:
            print(f"{username}: {message}")

    def simulate_ai_conversation(self, ai_user1, ai_user2, number_of_exchanges):
        """Simulates a conversation between two AI users."""
        for _ in range(number_of_exchanges):
            ai_user1.respond(self.forum)
            ai_user2.respond(self.forum)

# Test functions for the AIForum
def test_ai_forum():
    """
    Test function for the AIForum class.
    """
    ai_forum = AIForum()
    ai_forum.add_user_message("Alice", "Hi, this is Alice.")
    ai_forum.add_user_message("Bob", "Hello Alice, this is Bob.")
    ai_forum.display_forum_messages()


if __name__ == "__main__":
    # Running the test
    test_forum()
    test_ai_forum()