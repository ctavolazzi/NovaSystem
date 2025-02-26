# Weather MCP Server

This is a Model Context Protocol (MCP) server that provides weather data and forecasts using the OpenWeatherMap API.

## Prerequisites

- Python 3.10 or higher
- OpenWeatherMap API key
- uv package manager (install via `brew install uv` on macOS)

## Setup

1. Install uv if you haven't already:
```bash
brew install uv
```

2. Create a new virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
uv pip install -r requirements.txt
```

3. Install MCP SDK:
```bash
uv create-mcp-server --path .
```

4. Create a `.env` file with your OpenWeatherMap API key:
```bash
OPENWEATHER_API_KEY=your-api-key-here
```

5. Run the server:
```bash
python mcp-server.py
```

## Features

- Current weather data for any city
- Weather forecasts for 1-5 days
- Metric units for temperature and wind speed

## Resources

- `weather://{city}/current` - Get current weather for any city

## Tools

- `get_forecast` - Get weather forecast for a city
  - Parameters:
    - `city` (required): City name
    - `days` (optional): Number of days (1-5), defaults to 3

## Example Usage with Claude

```python
# Get current weather
weather = await read_resource("weather://London/current")
print(weather)

# Get forecast
forecast = await call_tool("get_forecast", {"city": "London", "days": 3})
print(forecast)
```