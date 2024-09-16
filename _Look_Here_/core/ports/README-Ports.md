# Port Module

The `Port` module provides classes for communication between bots in the NovaSystem.

## PortInterface

The `PortInterface` is an abstract base class defining the interface for communication ports.  It provides a consistent way to interact with different port implementations, regardless of the underlying protocol.

### Methods

* `send_data(data, destination)`: Sends `data` to the specified `destination`. The implementation of this method depends on the specific port adapter being used.
* `receive_data()`: Receives data from the port. The implementation of this method depends on the specific port adapter being used.
* `connect()`: Establishes a connection to the destination. The implementation of this method depends on the specific port adapter being used.
* `disconnect()`: Closes the connection to the destination. The implementation of this method depends on the specific port adapter being used.


## TCPPortAdapter

The `TCPPortAdapter` is a concrete implementation of the `PortInterface` that provides communication over TCP.

### Attributes

* `host`: The hostname or IP address of the destination.
* `port`: The port number to connect to.
* `socket`: The TCP socket object used for communication.

### Methods

* `send_data(data, destination)`:  Serializes the data (using JSON by default) and sends it to the specified `destination` over the TCP connection. It includes a length prefix to the data for proper message framing. 
* `receive_data()`: Receives data from the TCP socket. It reads the length prefix to determine the size of the incoming message and then receives the complete message. The received data is then deserialized (using JSON by default).
* `connect()`: Establishes a TCP connection to the specified host and port.
* `disconnect()`: Closes the TCP connection. 

### Error Handling

* If the `destination` is not valid, it raises an `InvalidDestinationError`.
* If there is an error sending or receiving data, it raises a `ConnectionError`.
