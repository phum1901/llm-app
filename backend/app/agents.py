import asyncio
import os
from textwrap import dedent

from pydantic_ai import Agent, RunContext

from app.mcp_servers import building_sensors, instruction_manual

technical_agent = Agent(
    name="technical_agent",
    model=os.getenv("MODEL_NAME"),
    result_retries=3,
    mcp_servers=[building_sensors],
    system_prompt=dedent(
        """
        You are a technical officer responsible for collecting data from sensors installed within a building.
        Your primary duty is to gather sensor readings accurately and consistently for further analysis.
        """  # noqa: E501
    ),
)

retrieval_agent = Agent(
    name="retrieval_agent",
    model=os.getenv("MODEL_NAME"),
    result_retries=3,
    mcp_servers=[instruction_manual],
    system_prompt=dedent(
        """
        You are an expert technician responsible for finding the most relevant documents from
        an instruction manual or handbook to help answer the query
        """  # noqa: E501
    ),
)

supervisor_agent = Agent(
    name="supervisor_agent",
    model=os.getenv("MODEL_NAME"),
    result_retries=5,
    end_strategy="exhaustive",
    system_prompt=dedent(
        """
        You are a supervisor coordinating the technical_agent and retrieval_agent.
        For each query:

        1. Use get_building_sensors if it involves current sensor data (e.g., temperature, CO2, humidity).
        2. Use retrieve_instruction_manual for procedures, protocols, or situational guidance.
        3. Always include actionable steps—consult the technical_agent when interpreting sensor data.
        4. For complex queries, use both tools in sequence.

        Your goal is to deliver complete, actionable answers by combining input from both agents when needed.
        """  # noqa: E501
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


async def run(query: str):
    async with technical_agent.run_mcp_servers(), retrieval_agent.run_mcp_servers():
        response = await supervisor_agent.run(query)
        return response.data


if __name__ == "__main__":
    asyncio.run(run())
