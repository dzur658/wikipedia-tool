import asyncio
import requests
from unstructured.partition.html import partition_html

# REPLACE YOUR USERAGGENT
# Wikimedia likes a descriptive User-Agent to keep track of who's using the service

class WikipediaToolKit:
    """
    A toolkit for LLMs to interact with the Wikimedia REST API.
    Initializes with a User-Agent to keep configuration hidden from the LLM.
    """
    def __init__(self, user_agent: str):
        # Store the headers at the instance level
        self.headers = {
            "User-Agent": user_agent
        }

    # wikipedia search
    async def search(self, query: str, limit: int = 5) -> str:
        """
        Search Wikipedia for a given query and return a formatted string of results suitable for LLM consumption.

        Args:
            query (str): The search query to look up on Wikipedia.
            limit (int): The maximum number of search results to return (default is 5).
        """
        url = "https://en.wikipedia.org/w/rest.php/v1/search/page"
        
        # Wikimedia requires a descriptive User-Agent
        headers = {
            "User-Agent": self.headers["User-Agent"]
        }
        
        params = {
            "q": query,
            "limit": limit
        }
        
        response = requests.get(url, headers=headers, params=params)

        # text block to give back to the llm instead of raw json
        llm_friendly = ""
        
        if response.status_code == 200:
            data = response.json()
            llm_friendly += f"--- Search Results for '{query}' ---\n"
            for page in data.get("pages", []):
                llm_friendly += f"Title: {page['title']}\n"
                llm_friendly += f"Description: {page.get('description', 'No description')}\n"
                llm_friendly += "-" * 20 + "\n"
        else:
            llm_friendly += f"Error: {response.status_code}\n"
            llm_friendly += response.text

        return llm_friendly

    # unstructured markdown extraction for articles
    async def parse_wikipedia_html(self, html_content: str) -> str:
        print("Parsing HTML with unstructured...")
        
        # We pass the raw string directly to the 'text' parameter
        elements = partition_html(text=html_content)
            
        # Now, let's filter out the junk and rebuild a clean document.
        # We only want the meaty parts: Titles, Narrative Text, and Lists.
        desired_categories = ["Title", "NarrativeText", "ListItem"]
        
        clean_paragraphs = []
        for el in elements:
            if type(el).__name__ in desired_categories:
                # We can clean up some common Wikipedia artifacts here if needed
                text = str(el).strip()
                if text:
                    clean_paragraphs.append(text)
                    
        # Join the clean elements with double newlines for excellent LLM readability
        final_markdown_ish_text = "\n\n".join(clean_paragraphs)
        
        return final_markdown_ish_text

    async def inspect(self, title: str) -> str:
        """Inspect a Wikipedia page by title and return the parsed content as markdown.
        
        Args:
            title (str): The title of the Wikipedia page to inspect. Pass the same value you receive from the search tool exactly, formatting will be automatically handled.
        """
        # sanitize spaces to underscores for the URL
        formatted_title = title.replace(" ", "_")
        
        # Pointing directly to the HTML endpoint instead of /bare
        url = f"https://en.wikipedia.org/w/rest.php/v1/page/{formatted_title}/html"
        
        headers = {
            "User-Agent": self.headers["User-Agent"]
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Because the response is raw HTML, we use .text instead of .json()
            html_content = response.text
            
            print(f"--- Raw HTML for '{title}' ---")
            
            markdown_content = await self.parse_wikipedia_html(html_content)

            # only return first 8k characters to not blow up context window
            return markdown_content[:8000]
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

async def main():
    # replace user agent for testing
    USER_AGENT = "[REPLACE ME]"

    wiki_tools = WikipediaToolKit(user_agent=USER_AGENT)

    # for testing purposes
    test_str = "Quantum computing"

    print(f"Searching Wikipedia for: {test_str}\n")
    search_results = await wiki_tools.search(test_str)
    print(search_results)
    # get first page
    print(f"\nInspecting Wikipedia page for: {test_str}\n")
    page_content = await wiki_tools.inspect(test_str)
    print(page_content)


if __name__ == "__main__":
    asyncio.run(main())
