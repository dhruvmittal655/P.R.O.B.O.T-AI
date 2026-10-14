import requests
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import re
import os


class ResearchDownloader:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def download_page(self, name, url, topic=None):
        """Fetch and parse content from a scientific research source API."""
        try:
            res = requests.get(url, headers=self.headers, timeout=12)
            if res.status_code != 200:
                print(f"Error fetching {name}: HTTP {res.status_code}")
                return None

            if name == "arXiv Papers":
                content = self.parse_arxiv(res.text)
            elif name == "OpenAlex Literature":
                content = self.parse_openalex(res.text)
            elif name == "PubMed Central":
                content = self.parse_pubmed(res.text)
            elif name == "Semantic Scholar":
                content = self.parse_semantic_scholar(res.text)
            else:
                from parser import Parser
                p = Parser()
                content = p.clean(res.text)

            if not content or len(content.strip()) < 30:
                return None

            return {
                "name": name,
                "url": url,
                "content": content
            }
        except Exception as e:
            print(f"Failed to download {name}: {e}")
            return None

    def parse_arxiv(self, xml_data):
        try:
            root = ET.fromstring(xml_data)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('atom:entry', ns)
            if not entries:
                return ""

            out = ["=== arXiv Scientific Papers & Preprints ===\n"]
            for i, entry in enumerate(entries, 1):
                title = entry.find('atom:title', ns)
                title_text = title.text.strip().replace("\n", " ") if title is not None else "Untitled Paper"
                summary = entry.find('atom:summary', ns)
                summary_text = summary.text.strip().replace("\n", " ") if summary is not None else "No summary available."
                
                authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns) if a.find('atom:name', ns) is not None]
                author_str = ", ".join(authors) if authors else "Unknown Authors"

                link = entry.find('atom:id', ns)
                link_str = link.text.strip() if link is not None else ""

                out.append(f"[{i}] {title_text}")
                out.append(f"Authors: {author_str}")
                if link_str:
                    out.append(f"URL: {link_str}")
                out.append(f"Abstract: {summary_text}\n")

            return "\n".join(out)
        except Exception as e:
            print("Error parsing arXiv XML:", e)
            return ""

    def parse_openalex(self, json_data):
        try:
            data = json.loads(json_data)
            results = data.get("results", [])
            if not results:
                return ""

            out = ["=== OpenAlex Academic Works & Open Access Literature ===\n"]
            for i, item in enumerate(results, 1):
                title = item.get("title") or "Untitled Work"
                
                # Reconstruct abstract from inverted index if present
                abs_index = item.get("abstract_inverted_index")
                abstract_text = "No summary available."
                if abs_index:
                    word_positions = []
                    for word, positions in abs_index.items():
                        for pos in positions:
                            word_positions.append((pos, word))
                    word_positions.sort(key=lambda x: x[0])
                    abstract_text = " ".join([w[1] for w in word_positions])

                authorships = item.get("authorships", [])
                authors = [a.get("author", {}).get("display_name", "") for a in authorships if a.get("author")]
                author_str = ", ".join([a for a in authors if a]) or "Various Researchers"

                pub_year = item.get("publication_year") or ""
                doi = item.get("doi") or ""

                out.append(f"[{i}] {title} ({pub_year})")
                out.append(f"Authors: {author_str}")
                if doi:
                    out.append(f"DOI/URL: {doi}")
                out.append(f"Abstract: {abstract_text[:1000]}\n")

            return "\n".join(out)
        except Exception as e:
            print("Error parsing OpenAlex JSON:", e)
            return ""

    def parse_pubmed(self, json_data):
        try:
            data = json.loads(json_data)
            id_list = data.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                return ""

            summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id={','.join(id_list)}&retmode=json"
            res = requests.get(summary_url, headers=self.headers, timeout=10)
            if res.status_code != 200:
                return ""

            sum_data = res.json().get("result", {})
            out = ["=== PubMed Central (PMC) Peer-Reviewed Biomedical & Science Articles ===\n"]
            count = 1
            for pmc_id in id_list:
                item = sum_data.get(pmc_id)
                if not item or isinstance(item, list):
                    continue
                title = item.get("title") or "Untitled PMC Article"
                pub_date = item.get("pubdate") or ""
                authors = [a.get("name", "") for a in item.get("authors", []) if isinstance(a, dict)]
                author_str = ", ".join(authors) if authors else "PMC Contributors"

                article_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/"

                out.append(f"[{count}] {title}")
                out.append(f"Authors: {author_str} | Date: {pub_date}")
                out.append(f"URL: {article_url}\n")
                count += 1

            return "\n".join(out)
        except Exception as e:
            print("Error parsing PubMed JSON:", e)
            return ""

    def parse_semantic_scholar(self, json_data):
        try:
            data = json.loads(json_data)
            papers = data.get("data", [])
            if not papers:
                return ""

            out = ["=== Semantic Scholar Research Papers ===\n"]
            for i, paper in enumerate(papers, 1):
                title = paper.get("title") or "Untitled Paper"
                abstract = paper.get("abstract") or "No abstract text provided."
                year = paper.get("year") or ""
                url = paper.get("url") or ""
                authors = [a.get("name") for a in paper.get("authors", []) if a.get("name")]
                author_str = ", ".join(authors) if authors else "Academic Authors"

                out.append(f"[{i}] {title} ({year})")
                out.append(f"Authors: {author_str}")
                if url:
                    out.append(f"URL: {url}")
                out.append(f"Abstract: {abstract[:1000]}\n")

            return "\n".join(out)
        except Exception as e:
            print("Error parsing Semantic Scholar JSON:", e)
            return ""
