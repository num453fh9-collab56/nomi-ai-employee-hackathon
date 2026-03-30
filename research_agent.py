import anthropic
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key="your-api-key-here"  # Replace with your API key
)

# Define tools for the research agent
tools = [
    {
        "name": "web_search",
        "description": "Searches the web for information about a topic. Returns a list of relevant URLs and snippets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "web_fetch",
        "description": "Fetches and extracts text content from a URL",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch content from"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "save_report",
        "description": "Saves the research report in structured format (JSON and Markdown)",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The research topic"
                },
                "summary": {
                    "type": "string",
                    "description": "Executive summary of findings"
                },
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of key findings"
                },
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of source URLs"
                }
            },
            "required": ["topic", "summary", "key_points", "sources"]
        }
    }
]

def web_search(query):
    """Simulated web search - in production, use Google Custom Search API or similar"""
    # For demo purposes, returning mock results
    # In production, integrate with real search API
    mock_results = {
        "AI agents": [
            {"url": "https://en.wikipedia.org/wiki/Intelligent_agent", "snippet": "An intelligent agent is a software entity that observes and acts upon an environment..."},
            {"url": "https://www.anthropic.com/research", "snippet": "Research on AI safety and capabilities..."}
        ],
        "default": [
            {"url": "https://example.com", "snippet": f"Information about {query}"}
        ]
    }

    results = mock_results.get(query, mock_results["default"])
    return {
        "results": results,
        "count": len(results)
    }

def web_fetch(url):
    """Fetch and extract text content from a URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        # Limit to first 2000 characters for the demo
        return {
            "url": url,
            "content": text[:2000],
            "length": len(text)
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e)
        }

def save_report(topic, summary, key_points, sources):
    """Save research report in both JSON and Markdown formats"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)

    # Prepare report data
    report_data = {
        "topic": topic,
        "timestamp": timestamp,
        "summary": summary,
        "key_points": key_points,
        "sources": sources
    }

    # Save as JSON
    json_filename = f"reports/research_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    # Save as Markdown
    md_filename = f"reports/research_{timestamp}.md"
    markdown_content = f"""# Research Report: {topic}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

{summary}

## Key Findings

"""
    for i, point in enumerate(key_points, 1):
        markdown_content += f"{i}. {point}\n"

    markdown_content += "\n## Sources\n\n"
    for source in sources:
        markdown_content += f"- {source}\n"

    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return {
        "json_file": json_filename,
        "markdown_file": md_filename,
        "status": "success"
    }

def execute_tool(tool_name, tool_input):
    """Execute the requested tool"""

    if tool_name == "web_search":
        return web_search(tool_input["query"])

    elif tool_name == "web_fetch":
        return web_fetch(tool_input["url"])

    elif tool_name == "save_report":
        return save_report(
            tool_input["topic"],
            tool_input["summary"],
            tool_input["key_points"],
            tool_input["sources"]
        )

    return {"error": "Unknown tool"}

def research_agent(topic):
    """Main research agent that autonomously researches a topic"""

    print(f"\n{'='*60}")
    print(f"🔍 RESEARCH AGENT STARTED")
    print(f"📋 Topic: {topic}")
    print(f"{'='*60}\n")

    # Initial prompt that guides the agent
    system_prompt = """You are a research agent. Your job is to:
1. Search for information about the given topic
2. Fetch and read relevant sources
3. Synthesize the information into key findings
4. Save a structured report

Be thorough but concise. Focus on the most important and accurate information."""

    messages = [
        {
            "role": "user",
            "content": f"Research this topic and create a comprehensive report: {topic}"
        }
    ]

    # Agent loop
    iteration = 0
    max_iterations = 10  # Prevent infinite loops

    while iteration < max_iterations:
        iteration += 1
        print(f"🔄 Iteration {iteration}")

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        # Check if agent wants to use tools
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    print(f"  🔧 Tool: {tool_name}")
                    print(f"     Input: {json.dumps(tool_input, indent=6)}")

                    result = execute_tool(tool_name, tool_input)
                    print(f"     ✓ Completed\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    })

            messages.append({"role": "user", "content": tool_results})

        else:
            # Agent is done
            final_response = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_response += block.text

            print(f"\n{'='*60}")
            print(f"✅ RESEARCH COMPLETE")
            print(f"{'='*60}\n")
            print(f"💬 Agent Response:\n{final_response}\n")

            return final_response

    print("⚠️ Max iterations reached")
    return "Research incomplete - max iterations reached"

# Example usage
if __name__ == "__main__":
    # Test the research agent
    research_agent("AI agents")
