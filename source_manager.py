import urllib.parse
from urllib.parse import urlparse
from ddgs import DDGS


class SourceManager:

    def get_sources(self, topic):
        """Build dynamic list of search targets for a topic."""
        topic_clean = topic.strip()
        topic_encoded = urllib.parse.quote(topic_clean)

        sources = [
            ("arXiv Papers", f"https://export.arxiv.org/api/query?search_query=all:{topic_encoded}&start=0&max_results=10"),
            ("OpenAlex Literature", f"https://api.openalex.org/works?search={topic_encoded}&per-page=10"),
            ("PubMed Central", f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term={topic_encoded}&retmode=json&retmax=10"),
            ("Semantic Scholar", f"https://api.semanticscholar.org/graph/v1/paper/search?query={topic_encoded}&limit=10&fields=title,abstract,authors,year,url"),
        ]

        return sources