import anthropic
import json
from datetime import datetime

# Initialize the Anthropic client
client = anthropic.Anthropic(
    api_key="your-api-key-here"  # Replace with your actual API key
)

# Define the tools our agent can use
tools = [
    {
        "name": "calculator",
        "description": "Performs basic math operations. Supports +, -, *, /",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate, e.g., '25 * 4 + 10'"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_current_time",
        "description": "Returns the current date and time",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Tool execution functions
def execute_tool(tool_name, tool_input):
    """Execute the requested tool and return results"""

    if tool_name == "calculator":
        try:
            # Safe evaluation of math expression
            result = eval(tool_input["expression"])
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    elif tool_name == "get_current_time":
        return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    return {"error": "Unknown tool"}

def run_agent(user_message):
    """Main agent loop"""

    messages = [{"role": "user", "content": user_message}]

    print(f"\n🤖 User: {user_message}\n")

    # Agent loop - continues until no more tool calls needed
    while True:
        # Call Claude with tools
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        # Check if Claude wants to use a tool
        if response.stop_reason == "tool_use":
            # Add Claude's response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Execute all tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    print(f"🔧 Using tool: {tool_name}")
                    print(f"   Input: {tool_input}")

                    # Execute the tool
                    result = execute_tool(tool_name, tool_input)
                    print(f"   Result: {result}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })

            # Send tool results back to Claude
            messages.append({"role": "user", "content": tool_results})

        else:
            # No more tools needed, get final response
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text

            print(f"💬 Agent: {final_text}\n")
            return final_text

# Example usage
if __name__ == "__main__":
    # Test the agent
    run_agent("What's 156 * 23 + 47?")
    run_agent("What time is it right now?")
    run_agent("Calculate 100 / 4 and tell me what time it is")
