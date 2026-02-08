// run.js
import { graphAI } from "graphai";
import fs from "fs";
import { createRequire } from 'module'; // For JSON imports if needed
import dotenv from 'dotenv';

dotenv.config();

const JINA_API_KEY = process.env.JINA_API_KEY;
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;

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