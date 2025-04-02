from mcp.server.fastmcp import FastMCP
import random
from typing import Dict, List

mcp = FastMCP("Building Sensors")

# Mock data storage
_sensor_data = {
    zone: {
        "co2": random.uniform(400, 1200),  # ppm
        "temperature": random.uniform(20, 25),  # Celsius
        "humidity": random.uniform(30, 60),  # %
        "occupancy": random.randint(0, 30),  # people
    }
    for zone in ["A", "B", "C", "D", "E", "F"]
}


@mcp.tool()
def get_zone_co2(zone: str) -> float:
    """Get the current CO2 level (in ppm) for a specific zone (A-F)"""
    if zone not in _sensor_data:
        raise ValueError(f"Invalid zone: {zone}. Must be one of A-F")
    # Simulate some variation in readings
    _sensor_data[zone]["co2"] += random.uniform(-50, 50)
    _sensor_data[zone]["co2"] = max(400, min(1500, _sensor_data[zone]["co2"]))
    return _sensor_data[zone]["co2"]


@mcp.tool()
def get_all_zones_co2() -> Dict[str, float]:
    """Get current CO2 levels (in ppm) for all zones"""
    return {zone: get_zone_co2(zone) for zone in _sensor_data.keys()}


@mcp.tool()
def get_zone_environmental_data(zone: str) -> Dict[str, float]:
    """Get all environmental data for a specific zone (A-F)"""
    if zone not in _sensor_data:
        raise ValueError(f"Invalid zone: {zone}. Must be one of A-F")

    # Update all sensor values with some random variation
    _sensor_data[zone]["temperature"] += random.uniform(-0.5, 0.5)
    _sensor_data[zone]["humidity"] += random.uniform(-2, 2)
    _sensor_data[zone]["occupancy"] += random.randint(-2, 2)

    # Ensure values stay within realistic ranges
    _sensor_data[zone]["temperature"] = max(
        18, min(28, _sensor_data[zone]["temperature"])
    )
    _sensor_data[zone]["humidity"] = max(20, min(70, _sensor_data[zone]["humidity"]))
    _sensor_data[zone]["occupancy"] = max(0, min(50, _sensor_data[zone]["occupancy"]))

    return _sensor_data[zone]


@mcp.tool()
def get_high_co2_zones(threshold: float = 1000.0) -> List[str]:
    """Get a list of zones where CO2 levels exceed the specified threshold (default 1000 ppm)"""
    high_co2_zones = []
    for zone in _sensor_data:
        if get_zone_co2(zone) > threshold:
            high_co2_zones.append(zone)
    return high_co2_zones


@mcp.resource("sensors://zones")
def get_available_zones() -> List[str]:
    """Get a list of all available sensor zones"""
    return list(_sensor_data.keys())


@mcp.resource("sensors://status")
def get_sensor_status() -> Dict[str, str]:
    """Get the current status of all sensors"""
    return {zone: "operational" for zone in _sensor_data.keys()}


if __name__ == "__main__":
    mcp.run(transport='sse')
