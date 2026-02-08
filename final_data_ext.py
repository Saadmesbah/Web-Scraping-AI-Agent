# pharmacy_extractor.py
import requests
from openai import OpenAI

JINA_API_KEY = "jina_85d6fa0450b145638da9c5253ee32b2bmEZKBA9IBXO0skxTTNMFYPSQ7WZY"
OPENROUTER_API_KEY = "api-key"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

def extract_pharmacy_data(url: str):
    """
    Given a pharmacy page URL, fetch content via Jina,
    then extract structured JSON using LLM.
    """
    try:
        # 1. Get cleaned content from Jina
        jina_request_url = f"https://r.jina.ai/{url}"
        headers = {
            'Authorization': f'Bearer {JINA_API_KEY}',
            'Accept': 'application/json'
        }

        response = requests.get(jina_request_url, headers=headers)
        response.raise_for_status()
        parsed_data = response.json()
        cleaned_text = parsed_data.get('data', {}).get('content', '')

        # 2. Send to LLM for structured extraction
        analysis_prompt = f"""
        From the following scraped pharmacy data, extract a JSON list of all pharmacies mentioned.
        
        {cleaned_text}
        
        Each pharmacy must be a dictionary with the following exact keys: 
        'name', 'address', 'phone_number', 'city', and 'link'.
        
        Rules:
        - 'name' is the pharmacy name (or location label if no name is found)
        - 'address' is the full address if available, else null
        - 'phone_number' is the full phone_number if available, else null
        - 'city' is the city name if available, else null
        - 'link' is the full URL to the pharmacy’s page if present, else null
        Return JSON ONLY, no text or explanation.
        """

        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        return completion.choices[0].message.content

    except Exception as e:
        return {"error": str(e)}