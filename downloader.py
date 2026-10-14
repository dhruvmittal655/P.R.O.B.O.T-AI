import requests
import urllib.parse
from parser import Parser


class Downloader:
    def __init__(self):

     self.parser = Parser()
    def get_research(self, topic):

     chunks = []

     lower = topic.lower()

     programming = [
        "python",
        "java",
        "c",
        "c++",
        "javascript",
        "html",
        "css",
        "sql",
        "machine learning",
        "deep learning"
    ]

     wiki = self.get_wikipedia(topic)

     if wiki:

        chunks.append({
            "title": "Wikipedia",
            "content": wiki
        })

     if any(word in lower for word in programming):

        gfg = self.get_gfg(topic)

        if gfg:

            chunks.append({
                "title": "GeeksforGeeks",
                "content": gfg
            })

     else:

        brit = self.get_britannica(topic)

        if brit:

            chunks.append({
                "title": "Britannica",
                "content": brit
            })

     arxiv = self.get_arxiv(topic)
     if arxiv:
        chunks.append({
            "title": "arXiv Papers",
            "content": arxiv
        })

     return chunks

    def get_arxiv(self, topic):
        """Fetch arXiv paper abstracts for the topic."""
        topic_clean = topic.strip()
        if not topic_clean:
            return ""
        url = f"https://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(topic_clean)}&start=0&max_results=3"
        try:
            from research_downloader import ResearchDownloader
            rd = ResearchDownloader()
            data = rd.download_page("arXiv Papers", url)
            if data:
                return data.get("content", "")
        except Exception as e:
            print("arXiv Downloader Error:", e)
        return ""

    def get_wikipedia(self, topic):

        """Return a Wikipedia extract, or an empty string when unavailable.

        Callers use truthiness to decide whether an article can be displayed
        and stored.  Returning a human-readable error message here made those
        messages look like valid articles and caused them to be cached.
        """

        topic = topic.strip()

        if not topic:
            return ""

        topic = urllib.parse.quote(topic)

        url = (
            "https://en.wikipedia.org/w/api.php"
            "?action=query"
            "&prop=extracts"
            "&explaintext=1"
            "&exsectionformat=wiki"
            "&redirects=1"
            "&format=json"
            "&titles=" + topic
        )

        headers = {
            "User-Agent": "SmartSearch/1.0 (Educational Project)"
        }

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )

            if response.status_code != 200:
                return ""

            data = response.json()

            pages = data.get("query", {}).get("pages", {})

            if not pages:
                return ""

            page = next(iter(pages.values()))

            extract = page.get("extract", "")

            if extract.strip() == "":
                return ""

            return extract

        except (requests.RequestException, ValueError, TypeError):
            return ""
    def get_gfg(self, topic):

     import requests
     from bs4 import BeautifulSoup
     import urllib.parse

     query = urllib.parse.quote(topic)

     url = f"https://www.geeksforgeeks.org/?s={query}"

     headers = {
        "User-Agent": "Mozilla/5.0"
    }

     try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        article = soup.find("article")

        if article:

            text = article.get_text(
                separator="\n",
                strip=True
            )

            return text[:5000]

     except:
        pass

     return ""

    def get_britannica(self, topic):

     import requests
     import urllib.parse

     query = urllib.parse.quote(topic)

     url = f"https://www.britannica.com/search?query={query}"

     headers = {
        "User-Agent": "Mozilla/5.0"
    }

     try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return ""

        return self.parser.clean(response.text)

     except:

        return ""
    def get_summary(self, topic):
     return self.get_wikipedia(topic)
