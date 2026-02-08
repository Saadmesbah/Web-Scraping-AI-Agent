import requests
from scrapegraphai.graphs import SmartScraperGraph
import json
import os


# 1) Point the OpenAI-compatible client to OpenRouter (env vars are the safest)
os.environ["OPENAI_API_KEY"] = "api-key"
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
#model
MODEL_ID = "deepseek/deepseek-chat-v3-0324:free"


JINA_API_KEY = "jina_85d6fa0450b145638da9c5253ee32b2bmEZKBA9IBXO0skxTTNMFYPSQ7WZY"
target_url = "https://www.annuaire-gratuit.ma/pharmacie-garde-casablanca/quartier-ain-chock.html"

# Use GET request correctly formatted as per your screenshot
jina_request_url = f"https://r.jina.ai/{target_url}"

headers = {
    'Authorization': f'Bearer {JINA_API_KEY}',
    'Accept': 'application/json'
}

# Fetch data from Jina with error handling
try:
    response = requests.get(jina_request_url, headers=headers, timeout=30)
    response.raise_for_status()
    
    # Check response (optional, but useful for debugging)
    parsed_data = response.json()
    cleaned_text = parsed_data.get('data', {}).get('content', '')
    
    if not cleaned_text:
        print("Warning: No content extracted from Jina API")
        cleaned_text = "No pharmacy data available from the website."

except requests.exceptions.HTTPError as e:
    print(f"Jina API Error: {e}")
    print("Jina service is currently unavailable. Using fallback text...")
    # Fallback text for testing the LLM functionality
    cleaned_text = ""

except requests.exceptions.RequestException as e:
    print(f"Network Error: {e}")
    print("Using fallback text for testing...")
    cleaned_text = ""

# Verify extracted text (optional debug step)
print(f"Content length: {len(cleaned_text)} characters")
print("First 200 characters:", cleaned_text[:200])

# Now send the cleaned text to ScrapeGraphAI + OpenRouter
OPENROUTER_API_KEY = "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"

graph_config = {
    "llm": {
        "model": MODEL_ID,
        "temperature": 0,
        
    },
    "verbose": True,
}

prompt = ("From the following web content, extract a JSON list of all pharmacies mentioned. "
    "Each pharmacy must be a dictionary with the following exact keys: 'name', 'address', and 'link'.\n"
    "- 'name' is the pharmacy name (or location label if no name is found)\n"
    "- 'address' is the full address if available, else null\n"
    "- 'link' is the full URL to the pharmacy's page if present, else null\n"
    "Return your answer as a JSON object with one key: 'pharmacies', and its value must be an array.\n"
    "Do NOT summarize. Do NOT group pharmacies by region. Do NOT add extra comments.\n"
    "Only extract data if an individual pharmacy is mentioned explicitly.\n"
    "If no pharmacy data is found, return: {\"pharmacies\": []}"
)

try:
    smart_scraper_graph = SmartScraperGraph(
        prompt=prompt,
        source=cleaned_text,
        config=graph_config
    )

    result = smart_scraper_graph.run()
    print(json.dumps(result, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"Error running SmartScraperGraph: {e}")
    print("This might be due to the ScrapeGraphAI library not supporting OpenRouter properly.")
    print("Try using the test_api.py approach instead.")
