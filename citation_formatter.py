import re


class CitationFormatter:
    """Utility class to format academic paper metadata into IEEE, APA 7, and BibTeX styles."""

    def clean_authors(self, raw_authors):
        if not raw_authors or raw_authors.lower() in ["unknown", "unknown author", "various researchers"]:
            return ["Unknown Author"]
        authors = [a.strip() for a in re.split(r'[,;]|\band\b', raw_authors) if a.strip()]
        return authors if authors else ["Unknown Author"]

    def format_ieee(self, title, authors="", year="2024", journal="Scientific Repository", url=""):
        auth_list = self.clean_authors(authors)
        if len(auth_list) == 1:
            auth_str = auth_list[0]
        elif len(auth_list) == 2:
            auth_str = f"{auth_list[0]} and {auth_list[1]}"
        else:
            auth_str = f"{auth_list[0]} et al."

        year_clean = str(year).strip() or "2024"
        journal_clean = journal.strip() if journal else "Scientific Repository"
        title_clean = title.strip().rstrip('.')

        citation = f'{auth_str}, "{title_clean}," {journal_clean}, {year_clean}.'
        if url:
            citation += f" Available: {url}"
        return citation

    def format_apa(self, title, authors="", year="2024", journal="Scientific Repository", url=""):
        auth_list = self.clean_authors(authors)
        formatted_authors = []
        for name in auth_list[:6]:
            parts = name.split()
            if len(parts) >= 2:
                last = parts[-1]
                initials = "".join([p[0].upper() + "." for p in parts[:-1]])
                formatted_authors.append(f"{last}, {initials}")
            else:
                formatted_authors.append(name)

        if len(auth_list) > 6:
            auth_str = ", ".join(formatted_authors[:6]) + ", ... " + formatted_authors[-1]
        elif len(formatted_authors) == 1:
            auth_str = formatted_authors[0]
        else:
            auth_str = ", ".join(formatted_authors[:-1]) + ", & " + formatted_authors[-1]

        year_clean = str(year).strip() or "2024"
        journal_clean = journal.strip() if journal else "Scientific Repository"
        title_clean = title.strip().rstrip('.')

        citation = f"{auth_str} ({year_clean}). {title_clean}. {journal_clean}."
        if url:
            citation += f" {url}"
        return citation

    def format_bibtex(self, title, authors="", year="2024", journal="Scientific Repository", url=""):
        auth_list = self.clean_authors(authors)
        auth_str = " and ".join(auth_list)
        year_clean = str(year).strip() or "2024"
        journal_clean = journal.strip() if journal else "Scientific Repository"
        title_clean = title.strip().rstrip('.')

        first_author_key = auth_list[0].split()[-1].lower() if auth_list else "author"
        clean_key = re.sub(r'[^a-zA-Z0-9]', '', first_author_key) + year_clean

        bibtex = (
            f"@article{{{clean_key},\n"
            f'  author = {{{auth_str}}},\n'
            f'  title = {{{{{title_clean}}}}},\n'
            f'  journal = {{{journal_clean}}},\n'
            f'  year = {{{year_clean}}}'
        )
        if url:
            bibtex += f',\n  url = {{{url}}}'
        bibtex += "\n}"
        return bibtex
