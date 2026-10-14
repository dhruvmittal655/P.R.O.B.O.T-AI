from bs4 import BeautifulSoup
import re


class Parser:

    def clean(self, text):

        if not text:
            return ""

        soup = BeautifulSoup(text, "html.parser")

        text = soup.get_text(separator="\n")

        text = re.sub(r"\n+", "\n", text)

        return text.strip()