# Simple Tool-Using Agent

Your first AI agent that can use tools to solve problems.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get your Anthropic API key:
   - Go to https://console.anthropic.com/
   - Create an account or sign in
   - Generate an API key
   - Replace `your-api-key-here` in `simple_agent.py` with your actual key

3. Run the agent:
```bash
python simple_agent.py
```

## How It Works

The agent follows this pattern:

1. **User asks a question** → "What's 156 * 23?"
2. **Claude decides which tool to use** → "I need the calculator tool"
3. **Tool executes** → Calculator returns 3588
4. **Claude responds** → "The answer is 3588"

## Current Tools

- `calculator`: Does math operations
- `get_current_time`: Returns current date/time

## Next Steps

Try adding your own tool:
- Weather lookup
- File reader
- Web scraper
- Database query

The pattern is always the same: define the tool schema, implement the execution function, add it to the tools list.
