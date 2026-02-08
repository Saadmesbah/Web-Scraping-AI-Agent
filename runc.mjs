const { graphAI } = require("graphai");
const fs = require("fs");

// Load environment variables (store these in .env)
const JINA_API_KEY = "jina_85d6fa0450b145638da9c5253ee32b2bmEZKBA9IBXO0skxTTNMFYPSQ7WZY";
const OPENROUTER_API_KEY = "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";

const runDiscovery = async () => {
  const discoveryGraph = fs.readFileSync("./discovery.yaml", "utf-8");
  const result = await graphAI(discoveryGraph, {
    JINA_API_KEY,
    OPENROUTER_API_KEY
  });
  return result.unique_links;
};

const scrapePharmacy = async (url) => {
  const scraperGraph = fs.readFileSync("./scraper.yaml", "utf-8");
  return await graphAI(scraperGraph, {
    JINA_API_KEY,
    OPENROUTER_API_KEY,
    params: { url }
  });
};

const main = async () => {
  try {
    // Step 1: Discover all pharmacy links
    const pharmacyLinks = await runDiscovery();
    console.log(`Found ${pharmacyLinks.length} pharmacies`);
    
    // Step 2: Scrape each pharmacy
    const results = [];
    for (const url of pharmacyLinks) {
      console.log(`Scraping ${url}...`);
      const { data_extractor } = await scrapePharmacy(url);
      results.push(data_extractor);
      
      // Throttle requests to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Save final results
    fs.writeFileSync("pharmaciess.json", JSON.stringify(results, null, 2));
    console.log("Scraping completed! Saved to pharmacies.json");
    
  } catch (error) {
    console.error("Scraping failed:", error);
  }
};

main();