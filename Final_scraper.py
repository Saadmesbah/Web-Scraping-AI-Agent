# link_extractor.py
from bs4 import BeautifulSoup
import requests
import networkx as nx
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque

def extract_links(root_url: str, max_pages: int = 1000, max_depth: int = 2):
    domain = urlparse(root_url).netloc

    REQUIRE = ("pharmacie",)
    ANY_OF = ("jour", "nuit", "garde24", "pharm", "pharmacie", "pharmacies",
              "garde", "de-garde", "de_garde", "officine", "parapharmacie",
              "parapharm", "para")

    def want(url: str) -> bool:
        u = url.lower()
        return all(x in u for x in REQUIRE) and any(y in u for y in ANY_OF)

    def normalize(u: str) -> str:
        return urldefrag(u)[0]

    visited = set()
    filtered_links = set()
    q = deque([(root_url, 0)])
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
            if want(full):
                filtered_links.add(full)
                if full not in visited and depth + 1 <= max_depth:
                    q.append((full, depth + 1))

    return sorted(filtered_links)

# Run standalone
if __name__ == "__main__":
    links = extract_links("https://www.annuaire-gratuit.ma/pharmacie-garde-maroc.html")
    print(f"Found {len(links)} links")
    with open("filtered_links.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(links))
