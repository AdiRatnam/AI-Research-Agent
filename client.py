import os
import sys
import asyncio
import time
import re
from contextlib import AsyncExitStack
from google import genai
from google.genai import types
from google.genai import errors
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def log_section(title):
    print("=" * 30)
    print(title)
    print("=" * 30 + "\n")

def log_round(round_num):
    print(f"Round {round_num}\n")

def log_separator():
    print("-" * 30 + "\n")

def convert_mcp_to_gemini_tool(mcp_tool):
    """Converts an MCP tool definition to a Gemini tool definition."""
    def clean_schema(schema):
        cleaned = {}
        for k, v in schema.items():
            if k == "type":
                cleaned[k] = v.upper()
            elif k == "properties":
                cleaned[k] = {pk: clean_schema(pv) for pk, pv in v.items()}
            elif k == "items":
                cleaned[k] = clean_schema(v)
            elif k == "required":
                cleaned[k] = v
            elif k == "description":
                cleaned[k] = v
        return cleaned
    
    clean_input_schema = clean_schema(mcp_tool.inputSchema)
    
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=mcp_tool.name,
                description=mcp_tool.description,
                parameters=types.Schema(**clean_input_schema)
            )
        ]
    )

def send_message_with_retry(chat, message, max_retries=5):
    """Sends a message to the chat with automatic retry on 429 Quota errors."""
    for attempt in range(max_retries):
        try:
            return chat.send_message(message)
        except errors.ClientError as e:
            if e.code == 429:
                print("\n[Rate limit exceeded. Checking retry delay...]")
                delay = 60 # Default wait time
                match = re.search(r"Please retry in ([0-9.]+)s", str(e))
                if match:
                    delay = float(match.group(1)) + 2.0
                print(f"[Sleeping for {delay:.1f} seconds to respect API rate limits...]\n")
                time.sleep(delay)
            else:
                raise e
    raise Exception("Max retries exceeded")

async def main():
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    log_section("MCP CLIENT")
    
    # Check for API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)
        
    llm_client = genai.Client()
    model_id = "gemini-3.6-flash"

    # Define how to start the server
    server_params = StdioServerParameters(
        command=os.path.join(".venv", "Scripts", "python.exe"),
        args=["server.py"],
        env=os.environ.copy()
    )
    
    async with AsyncExitStack() as stack:
        # connect to the server
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        
        # Get tools from server
        tools_response = await session.list_tools()
        mcp_tools = tools_response.tools
        gemini_tools = [convert_mcp_to_gemini_tool(t) for t in mcp_tools]
        
        user_prompt = """
        Research "Model Context Protocol (MCP)",
        prepare a concise research report,
        save it locally as mcp_report.md,
        and display it on a Prefab dashboard.
        """
        
        print(f"User Prompt:\n{user_prompt.strip()}\n")
        log_separator()
        
        chat = llm_client.chats.create(
            model=model_id,
            config=types.GenerateContentConfig(
                tools=gemini_tools,
                temperature=0.0
            )
        )

        round_num = 1
        log_round(round_num)
        print("Thinking...\n")
        
        response = send_message_with_retry(chat, user_prompt)
        
        while response.function_calls:
            for function_call in response.function_calls:
                tool_name = function_call.name
                
                # google-genai function_call.args is sometimes a dict, sometimes an object
                tool_args = function_call.args
                if hasattr(tool_args, "model_dump"):
                    tool_args = tool_args.model_dump()
                elif not isinstance(tool_args, dict):
                    tool_args = dict(tool_args)
                    
                print(f"Calling {tool_name}()\n")
                
                result = await session.call_tool(tool_name, tool_args)
                
                text_result = ""
                if result.content:
                    text_result = "\\n".join(c.text for c in result.content if c.type == "text")
                
                if not text_result:
                    text_result = "Success"
                    
                print(f"{text_result}\n")
                
                log_separator()
                round_num += 1
                log_round(round_num)
                print("Thinking...\n")
                
                response = send_message_with_retry(
                    chat,
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": text_result}
                    )
                )

        print("Mission Complete\n")
        print("Final Response:")
        print(response.text)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())


