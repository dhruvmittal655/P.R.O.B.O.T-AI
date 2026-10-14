import requests
import urllib.parse
from urllib.parse import urlparse
from ddgs import DDGS


class Searcher:

    def search(self, query):
        query = query.strip()
        url = (
            "https://en.wikipedia.org/w/api.php"
            "?action=opensearch"
            "&limit=10"
            "&namespace=0"
            "&format=json"
            "&search=" + urllib.parse.quote(query)
        )
        headers = {
            "User-Agent": "SmartSearch/1.0 (Educational Project)"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return []
            data = response.json()
            return data[1]
        except Exception:
            return []

    def get_suggestions(self, query):
        query = query.strip()
        url = (
            "https://en.wikipedia.org/w/api.php"
            "?action=opensearch"
            "&limit=5"
            "&namespace=0"
            "&format=json"
            "&search=" + urllib.parse.quote(query)
        )
        headers = {
            "User-Agent": "SmartSearch/1.0 (Educational Project)"
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code != 200:
                return []
            data = response.json()
            return data[1]
        except Exception:
            return []

    def find_site(self, topic, site):
        topic = topic.strip()
        site = site.strip().lower()
        if not topic or not site:
            return None
        query = f"{topic} site:{site}"
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
        except Exception as error:
            print(f"Source search failed for {site}: {error}")
            return None

        for result in results:
            href = result.get("href", "")
            hostname = urlparse(href).hostname
            if not hostname:
                continue
            hostname = hostname.lower()
            if hostname != site and not hostname.endswith("." + site):
                continue
            if "market.tutorialspoint.com" in href:
                continue
            return href
        return None

    def search_web_sources(self, topic, max_results=3):
        """Fetch top authoritative web search results dynamically for any topic."""
        topic = topic.strip()
        if not topic:
            return []
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{topic} overview research", max_results=max_results + 3))
        except Exception:
            return []

        sources = []
        for res in results:
            href = res.get("href", "")
            title = res.get("title", "")
            hostname = urlparse(href).hostname
            if not href or not hostname:
                continue
            hostname_clean = hostname.lower().replace("www.", "")
            if "wikipedia.org" in hostname_clean or "arxiv.org" in hostname_clean:
                continue
            site_name = title.split("-")[0].split("|")[0].strip() or hostname_clean.capitalize()
            sources.append((site_name, href))
            if len(sources) >= max_results:
                break
        return sources
