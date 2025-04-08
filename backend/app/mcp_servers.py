import os
from pydantic_ai.mcp import MCPServerStdio

building_sensors = MCPServerStdio(
    command="mcp", args=["run", "app/tools/sensors.py", "-t", "stdio"]
)

instruction_manual = MCPServerStdio(
    command="mcp",
    args=["run", "app/tools/instruction_manual.py", "-t", "stdio"],
    env={**os.environ},
)
