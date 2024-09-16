import time
from utils.generate_file_structure import generate_file_structure

def stc(message, delay=0.03):
  # Stream each character in a message to the console
  for char in message:
    print(char, end="", flush=True)
    time.sleep(delay)
  print()

def nova_say(message):
    # Use the stc function for NovaSystem AI speech
    stc(message)

def other_output(message):
    # Regular print statement for other outputs
    print(message)


#################################################################################################################################

def main():
  # Example usage
  nova_say("Hello, I am NovaSystem AI.")

  other_output("Standard system message.")

  root_directory = '/Users/ctavolazzi/Code/WinfoNova/Nova_System_Git/NovaSystem'
  output_filename = 'NovaSystem_file_structure.txt'
  generate_file_structure(root_directory, output_filename)


if __name__ == "__main__":
  main()