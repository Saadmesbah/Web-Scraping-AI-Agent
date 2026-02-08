from bs4 import BeautifulSoup
import requests
import networkx as nx
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque

root_url = "https://www.annuaire-gratuit.ma/pharmacie-garde-maroc.html"
domain = urlparse(root_url).netloc
max_pages, max_depth = 300, 2

# Filtering rules (keep your original logic: require "pharmacie" AND any of these)
REQUIRE = ("pharmacie",)
ANY_OF = ("jour", "nuit", "garde24", "pharm", "pharmacie", "pharmacies",
          "garde", "de-garde", "de_garde", "officine", "parapharmacie",
          "parapharm", "para")

def want(url: str) -> bool:
    u = url.lower()
    return all(x in u for x in REQUIRE) and any(y in u for y in ANY_OF)

def normalize(u: str) -> str:
    # drop fragments like #section
    return urldefrag(u)[0]

visited = set()
graph = nx.DiGraph()
filtered_links = set()

def crawl(start: str):
    q = deque([(start, 0)])
    headers = {"User-Agent": "Mozilla/5.0 (compatible; mini-crawler/1.0)"}

    while q and len(visited) < max_pages:
        url, depth = q.popleft()
        if url in visited or depth > max_depth:
            continue

        try:
            r = requests.get(url, timeout=5, headers=headers)
            if r.status_code != 200:
                continue
        except Exception:
            continue

        visited.add(url)
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.select("a[href]"):
            full = normalize(urljoin(url, a["href"]))
            if domain not in urlparse(full).netloc:
                continue

            # Only keep/follow links that match the keywords
            if want(full):
                filtered_links.add(full)
                graph.add_edge(url, full)
                if full not in visited and depth + 1 <= max_depth:
                    q.append((full, depth + 1))

crawl(root_url)

# Save filtered links
with open("filtered_links.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(filtered_links)))

# Quick stats
print({
    "Total nodes (pages)": len(graph.nodes),
    "Total edges (links)": len(graph.edges),
    "Filtered links saved": len(filtered_links),
    "Sample nodes": list(list(graph.nodes)[:5])
})
