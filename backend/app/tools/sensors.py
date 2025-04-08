import random

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Building Sensors")

# Mock data storage
sensor_data = {
    zone: {
        "co2": random.uniform(400, 1200),  # ppm
        "temperature": random.uniform(20, 25),  # Celsius
        "humidity": random.uniform(30, 60),  # %
        "occupancy": random.randint(0, 30),  # people
        "pm2.5": random.uniform(10, 50),  # µg/m³
    }
    for zone in ["A", "B", "C", "D", "E", "F"]
}


@mcp.tool()
def get_zone_pm25(zone: str) -> float:
    """Get the current PM2.5 level (in µg/m³) for a specific zone (A-F)"""
    if zone not in sensor_data:
        raise ValueError(f"Invalid zone: {zone}. Must be one of A-F")
    return sensor_data[zone]["pm2.5"] + random.uniform(0, 20)


@mcp.tool()
def get_zone_co2(zone: str) -> float:
    """Get the current CO2 level (in ppm) for a specific zone (A-F)"""
    if zone not in sensor_data:
        raise ValueError(f"Invalid zone: {zone}. Must be one of A-F")
    return sensor_data[zone]["co2"] + random.uniform(100, 100)


@mcp.tool()
def get_zone_temperature(zone: str) -> float:
    """Get the current temperature (in Celsius) for a specific zone (A-F)"""
    if zone not in sensor_data:
        raise ValueError(f"Invalid zone: {zone}. Must be one of A-F")
    return sensor_data[zone]["temperature"] + random.uniform(-3, 3)


@mcp.tool()
def get_zone_humidity(zone: str) -> float:
    """Get the current humidity (in %) for a specific zone (A-F)"""
    if zone not in sensor_data:
        raise ValueError(f"Invalid zone: {zone}. Must be one of A-F")
    return sensor_data[zone]["humidity"] + random.uniform(-10, 10)


@mcp.tool()
def get_zone_occupancy(zone: str) -> float:
    """Get the current occupancy (in people) for a specific zone (A-F)"""
    if zone not in sensor_data:
        raise ValueError(f"Invalid zone: {zone}. Must be one of A-F")
    return sensor_data[zone]["occupancy"] + random.randint(-2, 2)


@mcp.tool()
def get_zone_environmental_data(zone: str) -> dict[str, float]:
    """Get all environmental data for a specific zone (A-F)"""
    if zone not in sensor_data:
        raise ValueError(f"Invalid zone: {zone}. Must be one of A-F")

    # Update all sensor values with some random variation
    sensor_data[zone]["temperature"] += random.uniform(-3, 3)
    sensor_data[zone]["humidity"] += random.uniform(-10, 10)
    sensor_data[zone]["occupancy"] += random.randint(-2, 2)

    # Ensure values stay within realistic ranges
    sensor_data[zone]["temperature"] = max(
        18, min(28, sensor_data[zone]["temperature"])
    )
    sensor_data[zone]["humidity"] = max(20, min(70, sensor_data[zone]["humidity"]))
    sensor_data[zone]["occupancy"] = max(0, min(50, sensor_data[zone]["occupancy"]))

    return sensor_data[zone]


if __name__ == "__main__":
    mcp.run(transport="sse")
