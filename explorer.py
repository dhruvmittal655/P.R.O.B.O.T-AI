import re


class ResearchExplorer:

    def extract_sections(self, article):

        headings = []

        pattern = r'==\s*(.*?)\s*=='

        matches = list(re.finditer(pattern, article))

        if len(matches) == 0:

            return [{
                "title": "Full Article",
                "content": article
            }]

        sections = []

        for i, match in enumerate(matches):

            title = match.group(1)

            start = match.end()

            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(article)

            content = article[start:end].strip()

            sections.append({
                "title": title,
                "content": content
            })

        return sections