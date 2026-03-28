import asyncio
import requests
from unstructured.partition.html import partition_html

# REPLACE YOUR USERAGGENT
# Wikimedia likes a descriptive User-Agent to keep track of who's using the service


# wikipedia search
async def wikipedia_search(USER_AGENT, query: str, limit: int = 5):
    url = "https://en.wikipedia.org/w/rest.php/v1/search/page"
    
    # Wikimedia requires a descriptive User-Agent
    headers = {
        "User-Agent": USER_AGENT
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
async def parse_wikipedia_html(html_content: str):
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

async def wikipedia_inspect(USER_AGENT, title: str):
    # sanitize spaces to underscores for the URL
    formatted_title = title.replace(" ", "_")
    
    # Pointing directly to the HTML endpoint instead of /bare
    url = f"https://en.wikipedia.org/w/rest.php/v1/page/{formatted_title}/html"
    
    headers = {
        "User-Agent": USER_AGENT
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Because the response is raw HTML, we use .text instead of .json()
        html_content = response.text
        
        print(f"--- Raw HTML for '{title}' ---")
        
        markdown_content = await parse_wikipedia_html(html_content)

        # only return first 8k characters to not blow up context window
        return markdown_content[:8000]
        
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

async def main():
    # for testing purposes
    test_str = "Quantum computing"

    # replace user agent for testing
    USER_AGENT = "[REPLACE ME]"
    print(f"Searching Wikipedia for: {test_str}\n")
    search_results = await wikipedia_search(USER_AGENT, test_str)
    print(search_results)
    # get first page
    print(f"\nInspecting Wikipedia page for: {test_str}\n")
    page_content = await test_wikipedia_inspect(USER_AGENT, test_str)
    print(page_content)


if __name__ == "__main__":
    asyncio.run(main())
