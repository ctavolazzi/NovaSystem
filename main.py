import time

def stc(message, delay=0.22):
  # Stream each character in a message to the console
  for char in message:
    print(char, end="", flush=True)
    time.sleep(delay)
  print()

def main():
  stc("Hello World!")


if __name__ == "__main__":
  main()