import asyncio
import os

from agno.agent import Agent
from agno.models.google import Gemini
from agno.team.team import Team
from agno.tools.mcp import MCPTools


async def run(message: str):
    async with (
        MCPTools(command="mcp run app/tools/sensors.py -t stdio") as sensors,
        MCPTools(
            command="mcp run app/tools/instruction_manual.py -t stdio",
            env={**os.environ},
        ) as instruction_manual,
    ):
        technical = Agent(
            name="technical",
            description="You are a technical officer responsible for collecting data from sensors installed within a building.",  # noqa
            model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY")),
            tools=[sensors],
            markdown=True,
            show_tool_calls=True,
        )

        retrieval = Agent(
            name="retrieval",
            description="You are an expert technician responsible for finding the most relevant documents from an instruction manual or handbook to help answer the query",  # noqa
            model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY")),
            tools=[instruction_manual],
            markdown=True,
            show_tool_calls=True,
        )
        supervisor = Team(
            name="supervisor",
            model=Gemini(id="gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY")),
            mode="coordinate",
            description="You are a supervisor coordinating the technical and retrieval. Provides clear, actionable insights. When a user asks about sensor readings in a specific zone",  # noqa
            members=[technical, retrieval],
            enable_agentic_context=True,
            share_member_interactions=True,
            show_members_responses=True,
        )
        response = await supervisor.arun(message)
        return response.content


if __name__ == "__main__":
    # asyncio.run(run("what is the co2 level in zone A and the temperature in zone B"))
    # asyncio.run(run("what should we do if the co2 is above 1000ppm"))
    print(
        asyncio.run(run("what should we do if the temperature in zone A is above 30C"))
    )
