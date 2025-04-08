import os
import asyncio
from pydantic_ai import Agent, RunContext
from app.mcp_servers import building_sensors, instruction_manual


technical_agent = Agent(
    name="technical_agent",
    model=os.getenv("MODEL_NAME"),
    result_retries=3,
    mcp_servers=[building_sensors],
    system_prompt=(
        "You are a technical officer responsible for collecting data from sensors installed within a building.",
        "Your primary duty is to gather sensor readings accurately and consistently for further analysis.",
    ),
)

retrieval_agent = Agent(
    name="retrieval_agent",
    model=os.getenv("MODEL_NAME"),
    result_retries=3,
    mcp_servers=[instruction_manual],
    system_prompt=(
        "You are an expert technician responsible for finding the most relevant documents from an instruction manual or handbook to help answer the query"
    ),
)

supervisor_agent = Agent(
    name="supervisor_agent",
    model=os.getenv("MODEL_NAME"),
    result_retries=5,
    end_strategy="exhaustive",
    system_prompt=(
        "You are a supervisor responsible for orchestrating the collaboration between the technical_agent and retrieval_agent.",
        "For any incoming query:\n",
        "1. If the query involves getting current sensor readings (temperature, CO2, humidity, etc.), use get_building_sensors",
        # "2. If the query involves procedures, protocols, or what to do in certain situations, use retrieve_instruction_manual",
        "2. Respond must include actionable steps to take based on the sensor data you can get instructions from the technical_agent",
        # "3. For complex queries that need both sensor data and procedures, use both tools in sequence",
        "Your goal is to provide complete answers with actionable next steps by combining information from both agents when necessary.",
    ),
)


@supervisor_agent.tool()
async def get_building_sensors(ctx: RunContext, query: str) -> str:
    """Get the building sensors for a specific query"""
    result = await technical_agent.run(query, usage=ctx.usage)
    return f"Sensor Data: {result.data}"


@supervisor_agent.tool()
async def retrieve_instruction_manual(ctx: RunContext, query: str) -> str:
    """Retrieve the instruction manual for a specific query"""
    result = await retrieval_agent.run(query, usage=ctx.usage)
    return f"Manual Instructions: {result.data}"


async def main(query: str):
    async with technical_agent.run_mcp_servers(), retrieval_agent.run_mcp_servers():
        response = await supervisor_agent.run(query)
        return response.data


if __name__ == "__main__":
    asyncio.run(main())
