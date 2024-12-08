from websockets.sync.client import connect as ws_connect

def run_client():
    with ws_connect("ws://127.0.0.1:8765") as websocket:
        print("Connected to server")

        # Send initial message
        message = "Let's write a blog post about the benefits of AI pair programming."
        print(f"Sending message: {message}")
        websocket.send(message)

        # Receive responses
        while True:
            try:
                response = websocket.recv()
                response = response.decode("utf-8") if isinstance(response, bytes) else response
                print(response, end="", flush=True)
            except KeyboardInterrupt:
                print("\nDisconnecting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                break

if __name__ == "__main__":
    try:
        run_client()
    except KeyboardInterrupt:
        print("\nClient stopped")