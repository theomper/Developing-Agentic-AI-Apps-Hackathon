from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server - this automatically handles stdio transport
mcp = FastMCP("weather")

# Constants for the National Weather Service API
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling.

    This helper function handles HTTP requests to the National Weather Service
    API with proper headers and timeout configuration.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string.

    Takes a GeoJSON feature from the NWS API and extracts key
    alert information for display to the user.
    """
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    This tool queries the National Weather Service API for active severe weather
    alerts in the specified US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY, WA, TX)
    """
    # Construct URL to fetch alerts for the specified state
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    # Handle API errors or missing data
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    # Return appropriate message if no active alerts
    if not data["features"]:
        return "No active alerts for this state."

    # Format and join all alerts with a separator
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    This tool retrieves a detailed weather forecast for a specific geographic
    location using the National Weather Service API.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First, get the forecast grid endpoint for the given coordinates
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    # Handle errors fetching point data
    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Extract the forecast URL from the points response
    try:
        forecast_url = points_data["properties"]["forecast"]
    except KeyError:
        return "Unable to determine forecast URL for this location."

    # Fetch the actual forecast data
    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the forecast periods into readable text
    periods = forecast_data["properties"]["periods"]
    forecasts = []

    # Show the next 5 forecast periods
    for period in periods[:5]:
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

def main():
    """Initialize and run the MCP server.

    This starts the server listening on stdio, which allows MCP hosts
    (like Claude Desktop or VS Code) to communicate with it.
    """
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()