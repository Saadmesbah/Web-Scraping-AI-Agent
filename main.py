import Final_filter
import crawl as cr
import extract_pharmacy_data
import Final_scraper
import json
import subprocess


def run_pipeline(start_url):
    # 1. Run link extractor (your code may already write to file)
    print("🔗 Extracting links...")
    all_links = cr.crawl(start_url)

    # 2. Run filter_links.py via subprocess OR refactor into a function
    print("🧹 Filtering pharmacy links...")
    subprocess.run(["python", "filter_links.py"], check=True)

    # 3. Load filtered results
    with open("pharmacy_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    pharmacy_links = data.get("pharmacies", [])

    # 4. Extract pharmacy data from each page
    print(f"🏥 Extracting data from {len(pharmacy_links)} pharmacies...")
    all_pharmacies_data = []
    for link in pharmacy_links:
        result = extract_pharmacy_data(link)
        all_pharmacies_data.append(result)

    # 5. Save final JSON
    with open("pharmacies_full.json", "w", encoding="utf-8") as f:
        json.dump(all_pharmacies_data, f, ensure_ascii=False, indent=2)

    print("✅ Pipeline complete. Results saved to pharmacies_full.json")


if __name__ == "__main__":
    run_pipeline("https://www.annuaire-gratuit.ma")