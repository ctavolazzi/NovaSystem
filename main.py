from under_dev.NovaHelper import NovaHelper
import time

# Instantiate NovaHelper
helper = NovaHelper()

# Alias for helper.stc method
stc = helper.stc

# Display initial message
stc(f"You're a curious son of a bitch, aren't you?\n")

# Start the loading indicator
helper.start_loading_indicator()

# Allow the indicator to run for a few seconds (simulate some processing)
time.sleep(2)

# Stop the loading indicator
helper.stop_loading_indicator()

# Display second message
message = "Well, what do you want?"
stc(message)
