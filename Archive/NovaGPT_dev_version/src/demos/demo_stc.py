# src/demos/demo_stc.py

from src.utils.stream_to_console import stream_to_console as stc
import art

# ASCII Art
ascii_art = art.text2art("NovaSystem Demo")

# Stream the ASCII art first
stc(ascii_art, delay=0.01)

# Various demonstrations
demo_scenarios = [
    {"message": "Standard text", "delay": 0.03},
    {"message": "Fast text", "delay": 0.01},
    {"message": "Slow text", "delay": 0.1},
    {"message": "Red text", "foreground_color": "red"},
    # Add more scenarios here...
]

for scenario in demo_scenarios:
    stc(**scenario)

# Rainbow effect demonstration
stc("Rainbow Effect!", rainbow_effect=True)

# End of demo message
stc("Demo concluded. Thank you for watching!", delay=0.05)
