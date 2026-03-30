# Research Agent - AI Employee

An autonomous AI agent that researches topics, analyzes information, and generates structured reports.

## What It Does

1. **Searches** for information about your topic
2. **Fetches** content from relevant sources
3. **Analyzes** and synthesizes the information
4. **Saves** a structured report in JSON and Markdown

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add your Anthropic API key:
   - Open `research_agent.py`
   - Replace `your-api-key-here` with your actual API key from https://console.anthropic.com/

3. Run the agent:
```bash
python research_agent.py
```

## How to Use

Edit the last line in `research_agent.py`:

```python
research_agent("Your topic here")
```

Examples:
- `research_agent("AI agents")`
- `research_agent("Python async programming")`
- `research_agent("Digital marketing trends 2026")`

## Output

Reports are saved in the `reports/` folder:
- `research_TIMESTAMP.json` - Structured data
- `research_TIMESTAMP.md` - Human-readable report

## Example Workflow

```
User: research_agent("AI agents")
  ↓
Agent: Uses web_search tool → finds URLs
  ↓
Agent: Uses web_fetch tool → reads content
  ↓
Agent: Analyzes information → creates summary
  ↓
Agent: Uses save_report tool → saves files
  ↓
Done: Reports saved in reports/ folder
```

## Next Steps to Improve

1. **Add real search API** - Currently uses mock data. Integrate Google Custom Search or Bing API
2. **Add more sources** - Fetch from multiple URLs
3. **Better parsing** - Extract specific data types (stats, quotes, dates)
4. **Quality checks** - Verify information accuracy
5. **Cost tracking** - Monitor API usage

## Understanding the Code

**Key components:**
- `tools` - Defines what the agent can do
- `execute_tool()` - Runs the actual tool functions
- `research_agent()` - Main loop that lets Claude decide what to do next

The agent is **autonomous** - you just give it a topic, and it figures out the steps on its own.
