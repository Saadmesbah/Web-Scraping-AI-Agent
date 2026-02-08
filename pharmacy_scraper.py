import asyncio
from scrapegraphai.graphs import SmartScraperGraph
import json

async def scrape_pharmacy_data():
    """
    Test ScrapeGraphAI to scrape pharmacy data from the provided URL
    """
    
    # Initialize SmartScraperGraph with Ollama
    scraper = SmartScraperGraph(
        llm="ollama/llama3:8b",  # You can change this to your preferred model
        verbose=True
    )
    
    # The pharmacy URL to scrape
    url = "https://www.annuaire-gratuit.ma/pharmacies/pharmacie-zouan-s254027.html"
    
    # Define the data structure we want to extract
    schema = {
        "type": "object",
        "properties": {
            "pharmacy_name": {
                "type": "string",
                "description": "Name of the pharmacy"
            },
            "address": {
                "type": "string",
                "description": "Full address of the pharmacy"
            },
            "city": {
                "type": "string",
                "description": "City where the pharmacy is located"
            },
            "country": {
                "type": "string",
                "description": "Country where the pharmacy is located"
            },
            "phone_number": {
                "type": "string",
                "description": "Phone number of the pharmacy"
            },
            "reference": {
                "type": "string",
                "description": "Reference number of the pharmacy"
            },
            "coordinates": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate"
                    }
                }
            },
            "guard_schedule": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date of guard duty"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date of guard duty"
                        },
                        "type": {
                            "type": "string",
                            "description": "Type of guard duty (day, night, or both)"
                        }
                    }
                },
                "description": "List of guard duty schedules"
            },
            "rating": {
                "type": "object",
                "properties": {
                    "score": {
                        "type": "number",
                        "description": "Average rating score"
                    },
                    "total_reviews": {
                        "type": "integer",
                        "description": "Total number of reviews"
                    }
                }
            }
        },
        "required": ["pharmacy_name", "address", "city", "country", "phone_number"]
    }
    
    try:
        print(f"Starting to scrape pharmacy data from: {url}")
        print("=" * 60)
        
        # Scrape the data
        result = await scraper.scrape(
            url=url,
            schema=schema,
            instructions="""
            Extract comprehensive pharmacy information from this Moroccan pharmacy directory page.
            Pay special attention to:
            - Pharmacy name and contact details
            - Complete address information
            - Phone number
            - GPS coordinates if available
            - Guard duty schedules (pharmacies de garde)
            - Any ratings or reviews
            - Reference numbers
            """
        )
        
        print("\nScraping completed successfully!")
        print("=" * 60)
        
        # Display the results
        print("EXTRACTED PHARMACY DATA:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Save results to a JSON file
        with open("pharmacy_data.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\nData saved to: pharmacy_data.json")
        
        return result
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return None

async def test_simple_extraction():
    """
    Test a simpler extraction to verify the setup works
    """
    scraper = SmartScraperGraph(
        llm="ollama/llama3:8b",
        verbose=True
    )
    
    url = "https://www.annuaire-gratuit.ma/pharmacies/pharmacie-zouan-s254027.html"
    
    simple_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "phone": {"type": "string"},
            "address": {"type": "string"}
        }
    }
    
    try:
        print("Testing simple extraction...")
        result = await scraper.scrape(url=url, schema=simple_schema)
        print("Simple extraction result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"Simple extraction error: {str(e)}")
        return None

if __name__ == "__main__":
    print("ScrapeGraphAI Pharmacy Data Scraper")
    print("=" * 40)
    
    # First test with simple extraction
    print("\n1. Testing simple extraction...")
    simple_result = asyncio.run(test_simple_extraction())
    
    if simple_result:
        print("\n2. Testing comprehensive extraction...")
        # Then test with comprehensive extraction
        full_result = asyncio.run(scrape_pharmacy_data())
    else:
        print("Simple extraction failed. Please check your Ollama setup.")
