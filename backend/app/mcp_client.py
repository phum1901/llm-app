import os 
import asyncio
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from google import genai
from google.genai import types
from mcp import ClientSession, Tool
from mcp.client.sse import sse_client

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
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
            "object": "OBJECT"
        }
        
        parameters = {
            "type": "OBJECT",
            "properties": {},
            "required": []
        }

        # Access parameters through the tool's inputSchema
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            schema_properties = tool.inputSchema.get('properties', {})
            required_params = tool.inputSchema.get('required', [])
            
            for param_name, param_info in schema_properties.items():
                param_type = type_mapping.get(param_info.get('type', 'string'), "STRING")
                parameters["properties"][param_name] = {
                    "type": param_type,
                    "description": param_info.get('description', '')
                }
                if param_name in required_params:
                    parameters["required"].append(param_name)
        
        # If no properties were found, add a default 'input' parameter
        if not parameters["properties"]:
            parameters["properties"]["input"] = {
                "type": "STRING",
                "description": "Input for the tool"
            }
                
        return {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": parameters
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
    
    async def connect_to_server(self, server_url: str):
        # Create SSE transport and manage with exit stack
        streams = await self.exit_stack.enter_async_context(sse_client(server_url))
        
        # Create client session with read/write streams
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(streams[0], streams[1])
        )
        
        # Initialize the connection
        await self.session.initialize()
    
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        
        # Convert tools to Gemini format
        self.available_tools = self.get_gemini_tools(tools)
    
    async def process_query(self, query: str = "what is co2 in zone A?") -> str:
        """Process a query using Gemini and available tools"""
        messages = [
            types.UserContent([types.Part.from_text(text=query)])
        ]
        response = self.llm.models.generate_content(
            model='gemini-2.5-pro-exp-03-25',
            contents=messages,
            config=types.GenerateContentConfig(
                tools=self.available_tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False
            )
            )
        )

        final_text = []

        for part in response.candidates[0].content.parts:
            if part.text:
                final_text.append(part.text)
            elif part.function_call:
                tool_name = part.function_call.name
                tool_args = part.function_call.args
                result = await self.session.call_tool(tool_name, tool_args)
                print(result)
                if part.text:
                    messages.append(
                        types.ModelContent([types.Part.from_text(text=part.text)])
                    ) 
                messages.append(
                    types.Content(role='tool', parts=[types.Part.from_function_response(name=tool_name, response={'result': result.content})])
                ) 

                response = self.llm.models.generate_content(
                    model='gemini-2.5-pro-exp-03-25',
                    contents=messages,
                )

                final_text.append(response.text)

        return ''.join(final_text)

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

# async with sse_client("http://localhost:8000/sse") as streams:
#     async with ClientSession(streams[0], streams[1]) as session:
#         await session.initialize()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_url>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        # print(await client.process_query('what is co2 in zone A and environment data in zone B?'))
        print(await client.process_query('my name is phum.'))
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())