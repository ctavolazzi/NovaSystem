import asyncio
from port_factory import PortFactory

async def main():
    config = {
        "name": "MyWebSocketPort",
        "protocol": "websocket",
        "uri": "ws://localhost:8765"  # Replace with your WebSocket server URI
    }
    
    port = PortFactory().create_port(config)
    await port.connect()

    data_to_send = {"message": "Hello from Bot1!"}
    await port.send_data(data_to_send)

    # In a real application, this would be in a loop or task to receive messages continuously
    received_data = await port.receive_data()
    print(f"Received data: {received_data}")

    await port.disconnect()
