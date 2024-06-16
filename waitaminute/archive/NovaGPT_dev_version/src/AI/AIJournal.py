# src/AI/AIJournal.py
import os
import datetime
import logging

# Setting up basic logging
logging.basicConfig(level=logging.INFO, filename='ai_journal.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

class AIJournal:
    """
    AI Journal for recording conversation entries.

    Attributes:
        ai_name (str): Name of the AI.
        journal_path (str): Path to store journal entries.
    """

    def __init__(self, ai_name, journal_path="journals"):
        """
        Initialize the AI journal.

        Args:
            ai_name (str): Name of the AI.
            journal_path (str): Path to store journal entries. Defaults to 'journals'.
        """
        self.ai_name = ai_name
        self.journal_path = os.path.join(journal_path, ai_name)
        try:
            os.makedirs(self.journal_path, exist_ok=True)
        except Exception as e:
            logging.error(f"Error creating journal directory for {ai_name}: {e}")

    def create_journal_entry(self, title, location, content):
        """
        Create a journal entry.

        Args:
            title (str): The title of the conversation.
            location (str): The location where the conversation took place.
            content (str): The content of the journal entry.
        """
        try:
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = f"{self.ai_name}_{date_time.replace(':', '-')}.md"
            filepath = os.path.join(self.journal_path, filename)

            with open(filepath, 'w') as file:
                file.write(f"# {title}\n")
                file.write(f"**Date:** {date_time}\n")
                file.write(f"**Location:** {location}\n")
                file.write(f"## Entry\n")
                file.write(content + "\n")
            logging.info(f"Journal entry created for {self.ai_name}: {filepath}")
        except Exception as e:
            logging.error(f"Error creating journal entry for {self.ai_name}: {e}")

# Example Usage and Testing
def test_journal_entry():
    """
    Test function for creating a journal entry.
    """
    try:
        ai_journal = AIJournal("AI_Test_Bot")
        ai_journal.create_journal_entry("Test Conversation", "Test Location", "This is a test journal entry.")
        logging.info("Test journal entry created successfully.")
    except Exception as e:
        logging.error(f"Test journal entry failed: {e}")

if __name__ == "__main__":
    test_journal_entry()
