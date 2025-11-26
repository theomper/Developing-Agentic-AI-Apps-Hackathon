"""
Remote MCP Server for Azure Deployment - Challenge 04

This module implements an MCP server using FastAPI for HTTP transport,
making it suitable for deployment on Azure Container Apps or Azure Functions.

The server is containerized and runs as a web service, allowing remote
clients to access weather tools via HTTP instead of stdio.

⚠️  INCOMPLETE - You need to complete the implementation below
"""

from typing import Any
import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server with FastAPI
mcp = FastMCP("weather")

# Constants for the National Weather Service API
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling.

    This helper function handles HTTP requests to the National Weather Service
    API with appropriate headers, timeout, and error handling.

    Args:
        url: The full URL to request from the NWS API

    Returns:
        The parsed JSON response, or None if the request fails
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

    Args:
        feature: A weather alert feature from the NWS API

    Returns:
        A formatted string containing alert information
    """
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


# TODO: Implement the get_alerts tool
# ❌ Create an MCP tool that gets weather alerts for a US state
# Use the decorator: @mcp.tool()
# Parameters:
#   - state: Two-letter US state code (e.g., CA, NY, WA, TX)
# Return: String with formatted alerts or error message
# Steps:
#   1. Build the URL: f"{NWS_API_BASE}/alerts/active/area/{state}"
#   2. Call make_nws_request() to fetch data
#   3. Check if data exists and has "features"
#   4. If no features, return "No active alerts for this state."
#   5. Format each feature using format_alert()
#   6. Join alerts with "\n---\n" separator
# async def get_alerts(state: str) -> str:
#     pass
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

# TODO: Implement the get_forecast tool
# ❌ Create an MCP tool that gets weather forecast for a location
# Use the decorator: @mcp.tool()
# Parameters:
#   - latitude: float - Latitude of the location
#   - longitude: float - Longitude of the location
# Return: String with formatted forecast periods or error message
# Steps:
#   1. Build points URL: f"{NWS_API_BASE}/points/{latitude},{longitude}"
#   2. Call make_nws_request() to get points data
#   3. Extract forecast URL from points_data["properties"]["forecast"]
#   4. Call make_nws_request() with the forecast URL
#   5. Get the periods from forecast_data["properties"]["periods"]
#   6. Format each period (take first 5 periods)
#   7. Join periods with "\n---\n" separator
#   8. Handle errors gracefully with descriptive messages
# async def get_forecast(latitude: float, longitude: float) -> str:
#     pass
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


# TODO: Create FastAPI application
# ❌ Create a FastAPI app instance with title and version
app = FastAPI(title="Weather MCP Server", version="1.0.0")


# TODO: Implement health check endpoint
# ❌ Create a GET endpoint at "/health"
# Return: dict with {"status": "healthy", "service": "weather-mcp-server"}
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "weather-mcp-server"}


# TODO: Implement root information endpoint
# ❌ Create a GET endpoint at "/"
# Return: dict with server information including:
#   - name: "Weather MCP Server"
#   - version: "1.0.0"
#   - description: "MCP server providing weather forecasts and alerts"
#   - tools: list of available tools ["get_forecast", "get_alerts"]
#   - documentation: "/docs"
@app.get("/")
async def root():
    return {
        "name": "Weather MCP Server",
        "version": "1.0.0",
        "description": "MCP server providing weather forecasts and alerts",
        "tools": ["get_forecast", "get_alerts"],
        "documentation": "/docs"
    }


# TODO: Configure and run the server
# ❌ Add code to run the server when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )