import os
import re
import pypdf
from datetime import datetime


class PDFReader:
    """Utility class to read, extract text, and parse metadata from PDF documents."""

    def extract_pdf_details(self, pdf_path):
        """
        Extract text, page count, metadata, and executive abstract from a PDF file.
        Returns a dict containing:
        - title: Extracted title or filename
        - authors: Extracted author or 'Unknown Author'
        - page_count: Total page count
        - file_size: Human-readable file size
        - abstract: Executive summary / first page abstract
        - content: Full page-by-page extracted text
        """
        if not pdf_path or not os.path.exists(pdf_path):
            return None

        try:
            reader = pypdf.PdfReader(pdf_path)
            page_count = len(reader.pages)
            if page_count == 0:
                return None

            file_size_bytes = os.path.getsize(pdf_path)
            file_size = self._format_size(file_size_bytes)

            full_pages_text = []
            for i, page in enumerate(reader.pages, 1):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    full_pages_text.append(f"--- Page {i} ---\n{page_text.strip()}")

            full_content = "\n\n".join(full_pages_text)
            if not full_content.strip():
                return None

            # Attempt metadata extraction
            meta = reader.metadata or {}
            raw_title = meta.get("/Title") or meta.get("title") or ""
            raw_author = meta.get("/Author") or meta.get("author") or ""

            filename_clean = os.path.basename(pdf_path).rsplit(".", 1)[0].replace("_", " ").strip()
            title = str(raw_title).strip() if raw_title and len(str(raw_title).strip()) > 3 else filename_clean
            authors = str(raw_author).strip() if raw_author and len(str(raw_author).strip()) > 2 else "Unknown Author"

            # Extract executive abstract from first 2 pages
            first_pages_text = "\n".join([page.extract_text() or "" for page in reader.pages[:2]])
            abstract = self._extract_abstract(first_pages_text, full_content)

            return {
                "title": title,
                "authors": authors,
                "page_count": page_count,
                "file_size": file_size,
                "abstract": abstract,
                "content": full_content,
                "pub_date": datetime.now().strftime("%Y-%m-%d")
            }
        except Exception as ex:
            print(f"Error reading PDF {pdf_path}: {ex}")
            return None

    def _extract_abstract(self, first_pages_text, full_content):
        """Locate abstract section or return first 300 words."""
        match = re.search(r'(?i)\babstract\b[:\s\─\─\=]*([\s\S]{100,1200}?)(?=\n\s*(?:\d+\.?\s+introduction|\bkeywords\b|\b1\.\s+))', first_pages_text)
        if match:
            clean_abstract = match.group(1).strip().replace("\n", " ")
            if len(clean_abstract) > 50:
                return clean_abstract

        # Fallback: take first 1000 characters
        clean_full = re.sub(r'--- Page \d+ ---', '', full_content).strip().replace("\n", " ")
        return clean_full[:800] + "..." if len(clean_full) > 800 else clean_full

    def _format_size(self, bytes_size):
        """Format byte size into KB / MB string."""
        if bytes_size < 1024:
            return f"{bytes_size} Bytes"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        else:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
