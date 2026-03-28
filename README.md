# wikipedia-tool

A Python wrapper that allows an LLM to interact with Wikipedia content using the new Wikimedia API. It cleanly extracts and parses article text into an LLM-friendly format using the `unstructured` library.

## Installation

This project requires Python >= 3.12.

```bash
pip install https://github.com/dzur658/wikipedia-tool.git
```

*(If you are using `uv`, you can also use `uv pip install https://github.com/dzur658/wikipedia-tool.git`)*

## Usage as a Package

Once installed in your project, you can import the search and inspect functions to use as tools for your LLM. They are primarily meant to be used within the context of a ReAct agent for grounding purposes.

### Available Tools

1. **Search Tool (`wikipedia_search`)**: Searches Wikipedia for a query and returns an LLM-friendly formatted string containing page titles and short descriptions. This helps the agent discover relevant pages without loading massive amounts of text.
2. **Inspect Tool (`test_wikipedia_inspect`)**: Fetches a specific Wikipedia page by title, parsing the raw HTML to extract only relevant narrative text and lists. It returns a clean, chunked string optimized for LLM context windows.

### Example Integration

```python
import asyncio
# Import the tools into your project
from wikipedia_tool.main import wikipedia_search, wikipedia_inspect
import wikipedia_tool.main as wiki_main

# IMPORTANT: Override the default user agent for your specific project/contact info
wiki_main.USER_AGENT = "MyCoolAgentBot (myemail@example.com)"

async def agent_workflow():
    # 1. The agent uses the Search Tool to find relevant information
    query = "Quantum computing"
    print(f"--- Searching Wikipedia for: {query} ---")
    search_results = await wikipedia_search(query, limit=3)
    print(search_results)

    # 2. The agent decides to inspect a specific page title from the search results
    target_page = "Quantum computing"
    print(f"\n--- Extracting content for: {target_page} ---")
    page_content = await test_wikipedia_inspect(target_page)
    
    # Render the extracted content (truncated to fit context)
    print(page_content[:500] + "...\n[Content truncated]")

if __name__ == "__main__":
    asyncio.run(agent_workflow())
```
