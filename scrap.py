from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "model": "ollama/phi3:mini",
        "temperature": 0,
        "format": "json",
        "base_url": "http://localhost:11434",
        "model_tokens": 4096
    },
    "verbose": True,
    "headless": True,
       
}


prompt = (
  "Return ONLY a JSON object with key 'pharmacies' (array). "
  "Focus on the MAIN CONTENT of this page for the quartier named in the title (Aïn Chock). "
  "IGNORE all head/meta tags (og:title…), header, footer, nav, sidebars, social sections. "
  "For each pharmacy, include: name, address, phone, and absolute link if present. "
  "If none found, return {\"pharmacies\": []}."
)

smart = SmartScraperGraph(
    prompt=prompt,
    source="https://lematin.ma/pharmacie-garde-casablanca/jour/ain-chock",
    config=graph_config
)

result = smart.run()
print(result)
