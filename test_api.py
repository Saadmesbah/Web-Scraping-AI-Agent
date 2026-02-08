import requests
from openai import OpenAI

JINA_API_KEY = "API-key"
target_url = "https://www.annuaire-gratuit.ma/pharmacies/pharmacie-aloroba-s235205.html"



#Use GET request correctly formatted as per your screenshot
jina_request_url = f"https://r.jina.ai/{target_url}"

headers = {
    'Authorization': f'Bearer {JINA_API_KEY}',
    'Accept': 'application/json'
}

# Fetch data from Jina correctly (GET not POST)
response = requests.get(jina_request_url, headers=headers)
response.raise_for_status()

# Check response (optional, but useful for debugging)
parsed_data = response.json()
cleaned_text = parsed_data.get('data', {}).get('content', '')

print(cleaned_text)

#OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="API-key",
)

# Create a prompt that uses the cleaned_text
analysis_prompt = f"""
Based on the following scraped pharmacy data from Casablanca, please analyze and provide insights:

{cleaned_text}

Please provide:
"From the following web content, extract a JSON list of all pharmacies mentioned. "
    "Each pharmacy must be a dictionary with the following exact keys: 'name', 'address', 'phone_number', 'city', and 'link'.\n"
    "- 'name' is the pharmacy name (or location label if no name is found)\n"   
    "- 'address' is the full address if available, else null\n"
    "- 'phone_number' is the full phone_number if available, else null\n"
    "- 'city' is the city name if available, else null\n"
    "- 'link' is the full URL to the pharmacy’s page if present, else null\n"
    "Return your answer as a JSON object with one key: 'pharmacies', and its value must be an array.\n"
    "Do NOT summarize. Do NOT group pharmacies by region. Do NOT add extra comments.\n"
    "Only extract data if an individual pharmacy is mentioned explicitly.\n"
"""

completion = client.chat.completions.create(
  extra_body={},
  model="deepseek/deepseek-chat-v3-0324:free",
  messages=[
    {
      "role": "user",
      "content": analysis_prompt
    }
  ]
)
print(completion.choices[0].message.content)