# wikipedia-tool

A Python wrapper that allows an LLM to interact with Wikipedia content using the new Wikimedia API. It cleanly extracts and parses article text into an LLM-friendly format using the `unstructured` library.

## Installation

This project requires Python >= 3.12.

```bash
pip install https://github.com/dzur658/wikipedia-tool.git
```

*(If you are using `uv`, you can also use `uv pip install https://github.com/dzur658/wikipedia-tool.git`)*

## Usage

The tool provides asynchronous functions to search and inspect Wikipedia pages.
It is primarily meant to be used within the context of a ReAct agent for grounding purposes.

```python
import asyncio
from wikipedia_tool.main import wikipedia_search, test_wikipedia_inspect

async def main():
    query = "Quantum computing"
    
    # 1. Search Wikipedia (returns LLM-friendly string)
    search_results = await wikipedia_search(query, limit=3)
    print(search_results)

    # 2. Extract clean page content (parsed and chunked for LLMs)
    page_content = await test_wikipedia_inspect(query)
    print(page_content)

if __name__ == "__main__":
    asyncio.run(main())
```

> **Note:** Remember to update the `USER_AGENT` variable in `main.py` with your contact information (e.g., email), as Wikimedia requires a descriptive user-agent for API requests.
