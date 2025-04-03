import os
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from google import genai
from google.genai import types
from mcp import ClientSession, Tool
from mcp.client.sse import sse_client


class MCPClient:
    def __init__(self, url: str):
        self.url = url
        self.exit_stack = AsyncExitStack()
        self.llm = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    async def connect_to_server(self):
        read, write = await self.exit_stack.enter_async_context(sse_client(self.url))
        session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        return session

    async def process_query(self, query: str):
        session = await self.connect_to_server()
        tools_list = await session.list_tools()
        available_tools = self.get_gemini_tools(tools_list.tools)

        """Process a query using Gemini and available tools"""
        messages = [types.UserContent([types.Part.from_text(text=query)])]
        response = self.llm.models.generate_content(
            model="gemini-2.5-pro-exp-03-25",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=available_tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )

        final_text = []

        for part in response.candidates[0].content.parts:
            if part.text:
                final_text.append(part.text)
            elif part.function_call:
                tool_name = part.function_call.name
                tool_args = part.function_call.args
                result = await session.call_tool(tool_name, tool_args)
                print(result)
                if part.text:
                    messages.append(
                        types.ModelContent([types.Part.from_text(text=part.text)])
                    )
                messages.append(
                    types.Content(
                        role="tool",
                        parts=[
                            types.Part.from_function_response(
                                name=tool_name, response={"result": result.content}
                            )
                        ],
                    )
                )

                response = self.llm.models.generate_content(
                    model="gemini-2.5-pro-exp-03-25",
                    contents=messages,
                )

                final_text.append(response.text)

        return "".join(final_text)

    def _convert_mcp_tool_to_gemini(self, tool: Tool) -> Optional[Dict[str, Any]]:
        """Convert an MCP tool to Gemini function declaration format.

        Args:
            tool: MCP Tool object to convert

        Returns:
            Dict containing the Gemini function declaration, or None if the tool has no valid parameters
        """
        # Convert MCP parameter types to JSON Schema types
        type_mapping = {
            "string": "STRING",
            "number": "NUMBER",
            "integer": "NUMBER",
            "boolean": "BOOLEAN",
            "array": "ARRAY",
            "object": "OBJECT",
        }

        parameters = {"type": "OBJECT", "properties": {}, "required": []}

        # Access parameters through the tool's inputSchema
        if hasattr(tool, "inputSchema") and tool.inputSchema:
            schema_properties = tool.inputSchema.get("properties", {})
            required_params = tool.inputSchema.get("required", [])

            for param_name, param_info in schema_properties.items():
                param_type = type_mapping.get(
                    param_info.get("type", "string"), "STRING"
                )
                parameters["properties"][param_name] = {
                    "type": param_type,
                    "description": param_info.get("description", ""),
                }
                if param_name in required_params:
                    parameters["required"].append(param_name)

        # If no properties were found, add a default 'input' parameter
        if not parameters["properties"]:
            parameters["properties"]["input"] = {
                "type": "STRING",
                "description": "Input for the tool",
            }

        return {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": parameters,
        }

    def get_gemini_tools(self, mcp_tools: List[Tool]) -> List[types.Tool]:
        """Convert a list of MCP tools to Gemini tool format.

        Args:
            mcp_tools: List of MCP Tool objects

        Returns:
            List of Gemini Tool objects ready for function calling
        """
        function_declarations = [
            self._convert_mcp_tool_to_gemini(tool)
            for tool in mcp_tools
            if tool.name  # Only include tools with names
        ]

        if not function_declarations:
            return []

        return [types.Tool(function_declarations=function_declarations)]
