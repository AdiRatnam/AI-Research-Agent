from google import genai
from google.genai import types

mcp_schema = {
    "type": "object",
    "properties": {
        "topic": {"type": "string", "description": "The AI topic to research"}
    },
    "required": ["topic"]
}

try:
    schema = types.Schema(**mcp_schema)
    print("Success with dict unpacking!")
except Exception as e:
    print(f"Error: {e}")

try:
    upper_schema = {
        "type": "OBJECT",
        "properties": {
            "topic": types.Schema(type="STRING", description="The AI topic to research")
        },
        "required": ["topic"]
    }
    schema2 = types.Schema(**upper_schema)
    print("Success with upper case!")
except Exception as e:
    print(f"Error 2: {e}")
