import asyncio
from scrapegraphai.graphs import SmartScraperGraph
import json

async def test_scraper():
    # Basic configuration
    config = {
        "llm": {
            "provider": "ollama",
            "model": "llama3.2:3b",
            # Force deterministic, JSON-only output if supported by provider
            "temperature": 0,
            "format": "json"
        },
        "verbose": True
    }
    
    source = "https://www.annuaire-gratuit.ma/pharmacies/pharmacie-zouan-s254027.html"
    
    # Strict JSON-only prompt
    prompt = (
        "Extract pharmacy details from this page and return ONLY a valid JSON object with this exact schema. "
        "No explanation, no extra text, no markdown, no comments.\n\n"
        "Schema (keys and types):\n"
        "{\n"
        "  \"name\": string|null,\n"
        "  \"address\": string|null,\n"
        "  \"phone_number\": string|null,\n"
        "  \"city\": string|null,\n"
        f"  \"link\": \"{source}\"\n"
        "}\n\n"
        "Rules:\n"
        "- If a field is missing, set it to null.\n"
        "- Do not include any keys other than those in the schema.\n"
        "- Output must be a single JSON object only."
    )
    
    try:
        scraper = SmartScraperGraph(
            prompt=prompt,
            source=source,
            config=config
        )
        
        print("Scraper initialized successfully!")
        print("Running scraper...")
        
        result = await scraper.run_safe_async()
        
        print("Result:")
        if isinstance(result, (dict, list)):
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # Try to parse string to JSON if returned as raw text
            try:
                parsed = json.loads(result)
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            except Exception:
                print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraper())
