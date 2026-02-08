# filter_links.py
import sys, json
from openai import OpenAI

def filter_links(all_links, api_key: str, batch_size: int = 200):
    """
    Filters a list of URLs to keep only pharmacy detail pages using an LLM.
    
    Args:
        all_links (list[str]): candidate URLs
        api_key (str): OpenRouter API key
        batch_size (int): how many links to process per batch
    
    Returns:
        list[str]: pharmacy detail page URLs
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "pharmacy-link-filter"
        }
    )

    all_pharmacies = []

    for i in range(0, len(all_links), batch_size):
        batch = all_links[i:i + batch_size]
        batch_text = "\n".join(batch)
        
        print(f"Processing batch {i//batch_size + 1}/{(len(all_links) + batch_size - 1)//batch_size} ({len(batch)} links)")
        
        analysis_prompt = f"""
From the list of URLs below, return ONLY the pharmacy DETAIL PAGE links, not city or street index pages.

Examples:
- DETAIL (keep): https://www.annuaire-gratuit.ma/pharmacies/pharmacie-zouan-s254027.html
- CITY (drop):   https://www.annuaire-gratuit.ma/pharmacie-garde-casablanca.html
- STREET (drop): https://www.annuaire-gratuit.ma/pharmacie-garde-casablanca/quartier-ain-chock.html

Rules:
- Return JSON ONLY with this exact shape:
  {{ "pharmacies": ["<detail_url_1>", "<detail_url_2>", ...] }}
- No comments or prose.
- Only include URLs that clearly point to an individual pharmacy page.

URLs:
---
{batch_text}
---
""".strip()

        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324:free",
                temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": analysis_prompt}],
                timeout=120,
            )

            if not completion or not getattr(completion, "choices", None):
                print(f"API returned no choices for batch {i//batch_size + 1}. Skipping...", file=sys.stderr)
                continue

            msg = completion.choices[0].message
            content = (msg.content or "").strip()

            try:
                data = json.loads(content)
                if "pharmacies" in data and isinstance(data["pharmacies"], list):
                    all_pharmacies.extend(data["pharmacies"])
                    print(f"  Found {len(data['pharmacies'])} pharmacy links in this batch")
                else:
                    print(f"  No valid pharmacies found in batch {i//batch_size + 1}")
            except json.JSONDecodeError:
                print(f"  Model did not return valid JSON for batch {i//batch_size + 1}. Skipping...", file=sys.stderr)
                continue

        except Exception as e:
            print(f"API error for batch {i//batch_size + 1}: {repr(e)}", file=sys.stderr)
            continue

    return all_pharmacies


# Standalone mode
if __name__ == "__main__":
    with open("filtered_links.txt", "r", encoding="utf-8") as f:
        all_links = [line.strip() for line in f if line.strip()]

    print(f"Total links to process: {len(all_links)}")

    pharmacies = filter_links(all_links, api_key="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")
    final_data = {"pharmacies": pharmacies}

    with open("pharmacy_results.json", "w", encoding="utf-8") as output_file:
        json.dump(final_data, output_file, ensure_ascii=False, indent=2)

    print(f"\nProcessing complete!")
    print(f"Total pharmacy links found: {len(pharmacies)}")
    print("Results saved to pharmacy_results.json")
    print(json.dumps(final_data, ensure_ascii=False, indent=2))
