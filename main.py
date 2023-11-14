import time

def stc(message):
  # Stream each character in a message to the console
  for char in message:
    print(char, end="")
    time.sleep(0.1)
  print()

def main():
  stc("Hello World!")


if __name__ == "__main__":
  main()