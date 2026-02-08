import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from scrapegraphai.graphs import SmartScraperGraph

CONCURRENCY_LIMIT = 5
CHECKPOINT_EVERY = 50
OUTPUT_FILE = "detailed_pharmacies_scrapegraph.json"
CHECKPOINT_FILE = "detailed_pharmacies_scrapegraph.checkpoint.json"
FAILED_FILE = "failed_urls_scrapegraph.json"

# Configure the LLM provider. Using local Ollama by default for $0.
LLM_CONFIG = {
    "llm": {
        "provider": "ollama",
        "model": "llama3.2:3b",
        "temperature": 0,
        "format": "json"
    },
    "verbose": True,
}

SCHEMA_KEYS = ["name", "address", "phone_number", "city", "link"]


def build_prompt(page_url: str) -> str:
    return (
        "Extract pharmacy details from this page and return ONLY a valid JSON object with this exact schema. "
        "No explanation, no extra text, no markdown, no comments.\n\n"
        "Schema (keys and types):\n"
        "{\n"
        "  \"name\": string|null,\n"
        "  \"address\": string|null,\n"
        "  \"phone_number\": string|null,\n"
        "  \"city\": string|null,\n"
        f"  \"link\": \"{page_url}\"\n"
        "}\n\n"
        "Rules:\n"
        "- If a field is missing, set it to null.\n"
        "- Do not include any keys other than those in the schema.\n"
        "- Output must be a single JSON object only."
    )


async def scrape_one(url: str, sem: asyncio.Semaphore) -> Dict[str, Any]:
    prompt = build_prompt(url)

    async with sem:
        scraper = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=LLM_CONFIG,
        )
        result = await scraper.run_safe_async()

    # Normalize to dict and ensure schema
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except Exception:
            return {"ok": False, "url": url, "error": "Non-JSON response"}

    if not isinstance(result, dict):
        return {"ok": False, "url": url, "error": "Unexpected result type"}

    # Keep only expected keys; fill missing with null
    normalized: Dict[str, Any] = {k: result.get(k) if k in result else None for k in SCHEMA_KEYS}
    normalized["link"] = url  # enforce link

    return {"ok": True, "data": normalized}


def load_urls() -> List[str]:
    with open("pharmacy_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    urls = data.get("pharmacies", [])
    # Deduplicate while preserving order
    seen = set()
    ordered: List[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    return ordered


def save_checkpoint(done: List[Dict[str, Any]], failed: List[Dict[str, Any]]):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({"pharmacies": done, "failed": failed}, f, ensure_ascii=False, indent=2)


async def main():
    urls = load_urls()
    print(f"Total URLs: {len(urls)}")

    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

    results: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []

    async def runner(u: str):
        try:
            r = await scrape_one(u, sem)
            return (u, r)
        except Exception as e:
            return (u, {"ok": False, "url": u, "error": str(e)})

    # Process in waves for backpressure-friendly logging
    BATCH = 100
    for start in range(0, len(urls), BATCH):
        batch = urls[start:start + BATCH]
        print(f"Running batch {start + 1}-{start + len(batch)}...")
        tasks = [asyncio.create_task(runner(u)) for u in batch]
        for idx, task in enumerate(asyncio.as_completed(tasks), 1):
            url, outcome = await task
            if outcome.get("ok"):
                results.append(outcome["data"]) 
                print(f"  ✓ [{len(results)}/{len(urls)}] OK: {url}")
            else:
                failed.append({"url": url, "error": outcome.get("error", "unknown")})
                print(f"  ✗ [{len(results)+len(failed)}/{len(urls)}] FAIL: {url} -> {outcome.get('error')}")

            if (len(results) + len(failed)) % CHECKPOINT_EVERY == 0:
                save_checkpoint(results, failed)

        # Save after each batch
        save_checkpoint(results, failed)

    final = {
        "total_processed": len(urls),
        "successful_extractions": len(results),
        "failed_extractions": len(failed),
        "pharmacies": results,
        "failed_urls": failed,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    with open(FAILED_FILE, "w", encoding="utf-8") as f:
        json.dump(failed, f, ensure_ascii=False, indent=2)

    print("\nDone.")
    print(f"Saved: {OUTPUT_FILE}")
    print(f"Checkpoint: {CHECKPOINT_FILE}")
    print(f"Failed list: {FAILED_FILE}")


if __name__ == "__main__":
    asyncio.run(main())






