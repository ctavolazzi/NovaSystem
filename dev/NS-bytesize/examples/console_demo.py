from utils.console import NovaConsole
import time

def demonstrate_console():
    # Initialize console with timestamps and debug mode
    console = NovaConsole(show_timestamp=True, debug=True)

    # Clear the console
    console.clear()

    # System startup messages
    console.system("NovaSystem Console Demo Starting")
    console.debug("Debug mode enabled")

    # Information messages
    console.info("Initializing system components")
    console.info("Loading configuration", detail={"config_path": "/etc/nova/config.json"})

    # Simulated progress bar
    total_steps = 5
    for i in range(total_steps + 1):
        console.progress(i, total_steps, prefix="Loading", suffix="Please wait...")
        time.sleep(0.5)

    # Success message
    console.success("System components initialized successfully")

    # Warning example
    console.warning("CPU usage above 80%", detail={"usage": "85%", "threshold": "80%"})

    # Error example with exception detail
    try:
        raise ValueError("Sample error")
    except Exception as e:
        console.error("An error occurred", detail=str(e))

    # Debug information
    console.debug("Memory usage", detail={"total": "8GB", "used": "4.2GB", "free": "3.8GB"})

    # System shutdown
    console.system("NovaSystem Console Demo Complete")

if __name__ == "__main__":
    demonstrate_console()