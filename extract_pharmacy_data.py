import requests
import json
import time
import sys
from openai import OpenAI

JINA_API_KEY = "API-key"

# OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="API-Key",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "pharmacy-data-extractor"
    }
)

# 1) Load pharmacy URLs from results
with open("pharmacy_results.json", "r", encoding="utf-8") as f:
    pharmacy_data = json.load(f)

pharmacy_urls = pharmacy_data.get("pharmacies", [])
print(f"Found {len(pharmacy_urls)} pharmacy URLs to process")

# 2) Process each pharmacy
all_pharmacies_data = []
failed_urls = []

for i, url in enumerate(pharmacy_urls, 1):
    print(f"Processing {i}/{len(pharmacy_urls)}: {url}")
    
    try:
        # Fetch data from Jina
        jina_request_url = f"https://r.jina.ai/{url}"
        headers = {
            'Authorization': f'Bearer {JINA_API_KEY}',
            'Accept': 'application/json'
        }
        
        response = requests.get(jina_request_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        parsed_data = response.json()
        cleaned_text = parsed_data.get('data', {}).get('content', '')
        
        if not cleaned_text.strip():
            print(f"  ⚠️  No content found for {url}")
            failed_urls.append({"url": url, "error": "No content found"})
            continue
        
        # Extract pharmacy data using OpenAI
        analysis_prompt = f"""
Extract pharmacy information from this web page content. Return ONLY a JSON object with this exact structure:

{{
    "name": "pharmacy name or null if not found",
    "address": "full address or null if not found", 
    "phone_number": "phone number or null if not found",
    "city": "city name or null if not found",
    "link": "{url}"
}}

Rules:
- Extract only if this is clearly a pharmacy page
- Return null for fields that are not found
- Keep the original URL as the link
- No comments or explanations, just the JSON

Page content:
---
{cleaned_text[:8000]}  # Limit content to avoid token issues
---
""".strip()

        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": analysis_prompt}],
            timeout=60,
        )
        
        if completion and completion.choices:
            content = completion.choices[0].message.content.strip()
            try:
                pharmacy_info = json.loads(content)
                pharmacy_info["link"] = url  # Ensure URL is preserved
                all_pharmacies_data.append(pharmacy_info)
                print(f"  ✅ Extracted: {pharmacy_info.get('name', 'Unknown')}")
            except json.JSONDecodeError:
                print(f"  ❌ Failed to parse JSON for {url}")
                failed_urls.append({"url": url, "error": "JSON parse error"})
        else:
            print(f"  ❌ No response from API for {url}")
            failed_urls.append({"url": url, "error": "No API response"})
            
    except requests.RequestException as e:
        print(f"  ❌ Request failed for {url}: {e}")
        failed_urls.append({"url": url, "error": f"Request failed: {e}"})
    except Exception as e:
        print(f"  ❌ Unexpected error for {url}: {e}")
        failed_urls.append({"url": url, "error": f"Unexpected error: {e}"})
    
    # Add delay to avoid rate limiting
    time.sleep(1)

# 3) Save results
final_results = {
    "total_processed": len(pharmacy_urls),
    "successful_extractions": len(all_pharmacies_data),
    "failed_extractions": len(failed_urls),
    "pharmacies": all_pharmacies_data,
    "failed_urls": failed_urls
}

with open("detailed_pharmacies.json", "w", encoding="utf-8") as f:
    json.dump(final_results, f, ensure_ascii=False, indent=2)

print(f"\n🎉 Processing complete!")
print(f"✅ Successfully processed: {len(all_pharmacies_data)} pharmacies")
print(f"❌ Failed: {len(failed_urls)} URLs")
print(f"📁 Results saved to: detailed_pharmacies.json")

# Show sample of extracted data
if all_pharmacies_data:
    print(f"\n📋 Sample extracted data:")
    print(json.dumps(all_pharmacies_data[0], ensure_ascii=False, indent=2))
