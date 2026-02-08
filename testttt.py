import requests
from scrapegraphai.graphs import SmartScraperGraph

# Custom LLM function for OpenRouter
def openrouter_llm_call(prompt: str, api_key: str, model: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/Saadmesbah",  # Required by OpenRouter
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )
    return response.json()["choices"][0]["message"]["content"]

# Configure ScrapeGraphAI with OpenRouter
llm_config = {
    "llm": {  # <-- Must include "llm" key for ScrapeGraphAI
        "api_key": "api-key",  # Your OpenRouter API key
        "model": "deepseek-chat-v3-0324",
        "llm_fetch_function": lambda prompt: openrouter_llm_call(
            prompt, 
            "api-key",  # API key again (or use a variable)
            "deepseek-chat-v3-0324"
        )
    }
}

# Define the scraper
smart_scraper = SmartScraperGraph(
    prompt="Extract all article titles and summaries from this page",
    source="https://docs.scrapegraphai.com/introduction",
    config=llm_config  # Pass the properly structured config
)

# Run the scraper
result = smart_scraper.run()
print(result)