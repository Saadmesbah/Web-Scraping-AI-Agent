from typing import List
from pydantic import BaseModel, Field
from scrapegraphai.graphs import SmartScraperGraph
import json, pathlib

class Pharmacy(BaseModel):
    name: str   = Field(description="Pharmacy name from the <h3>")
    address: str= Field(description="Address sentence under the name")
    phone: str  = Field(description="Digits after 'Téléphone'")
    url: str    = Field(description="Link inside the <h3>")

class Pharmacies(BaseModel):
    pharmacies: List[Pharmacy] = []

cfg = {
    "llm": {
        "model": "ollama/gemma3:4b",  # or ollama/llama3:8b (slower, stronger)
        "temperature": 0,
        "format": "json",
        "num_predict": 200,
        "num_ctx": 2048,
        "model_tokens": 8192
    },
    "headless": True,
    "verbose": True,
    "timeout": 900
}

prompt = """
You are extracting pharmacies from a French directory page.
Each entry is a <li class="col-xs-12 ag_listing_item column_in_grey">.
For each item:
- name = <h3> text
- url  = the <a> href inside that <h3>
- address = first <p> paragraph under the name
- phone = number shown after label "Téléphone"
If a field is missing, use an empty string.
Return ONLY JSON for the schema.
"""

graph = SmartScraperGraph(
    prompt=prompt,
    source="https://www.annuaire-gratuit.ma/pharmacie-garde-marrakech.html",
    config=cfg,
    schema=Pharmacies,
)

result = graph.run()
print(result)  # should be {'pharmacies': [...]}

# save to file
pathlib.Path("pharmacies.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print("Saved to pharmacies.json")