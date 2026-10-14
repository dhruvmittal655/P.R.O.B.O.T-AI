import re
from collections import Counter

class NotesGenerator:

    def generate_notes(self, title, article):

     article = article.replace("\n", " ").strip()

     sentences = re.split(r'(?<=[.!?])\s+', article)
     sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

    # ================= OVERVIEW =================

     overview = " ".join(sentences[:3])

    # ================= KEY POINTS =================

     key_points = []
     seen = set()
 
     for sentence in sentences:

        sentence = re.sub(r"\[[^\]]*\]", "", sentence)

        if "," in sentence:
            sentence = sentence.split(",")[0]

        if ";" in sentence:
            sentence = sentence.split(";")[0]

        sentence = sentence.strip()

        if len(sentence) < 40:
            continue

        if sentence in seen:
            continue

        seen.add(sentence)
        key_points.append(sentence)

        if len(key_points) == 6:
            break

    # ================= KEYWORDS =================

     stop_words = {
        "the","and","of","to","in","a","is","was","for",
        "with","on","as","by","an","that","this","it",
        "from","at","be","are","or","his","her","their",
        "have","has","had","also"
    }

     words = re.findall(r"\b[A-Za-z][A-Za-z\-]+\b", article)

     words = [
        w for w in words
        if len(w) > 3
        and w.lower() not in stop_words
        and w.lower() != title.lower()
    ]

     counter = Counter(words)

     keywords = []

     for word, count in counter.most_common():

        if count < 2:
            continue

        keywords.append(word)

        if len(keywords) == 10:
            break

    # ================= IMPORTANT FACTS =================

     facts = []

     years = sorted(set(re.findall(r"\b(1[89]\d{2}|20\d{2})\b", article)))

     if years:
        facts.append("Important Years: " + ", ".join(years[:5]))

     creator = re.search(r"created by ([^.]+)", article, re.IGNORECASE)

     if creator:
        facts.append("Created by: " + creator.group(1).strip())

     publisher = re.search(r"published by ([^.]+)", article, re.IGNORECASE)

     if publisher:
        facts.append("Publisher: " + publisher.group(1).strip())

     alias = re.search(r"alias of ([^.]+)", article, re.IGNORECASE)

     if alias:
        facts.append("Alias: " + alias.group(1).strip())

     debut = re.search(r"debuted[^.]*?(\d{4})", article, re.IGNORECASE)

     if debut:
        facts.append("First Appearance: " + debut.group(1))
    # ================= DID YOU KNOW =================

     did_you_know = []

     if debut:
      did_you_know.append(
        f"{title} first appeared in {debut.group(1)}."
    )

     if creator:
       did_you_know.append(
        f"{title} was created by {creator.group(1).strip()}."
    )

     if publisher:
       did_you_know.append(
        f"It is published by {publisher.group(1).strip()}."
    )

     if alias:
      did_you_know.append(
        f"The real identity is {alias.group(1).strip()}."
    )

     if len(sentences) > 8:
      did_you_know.append(sentences[8]) 
    # ================= EXAM QUESTIONS =================

     questions = [
        f"What is {title}?"
    ]

     if creator:
        questions.append(f"Who created {title}?")

     if publisher:
        questions.append(f"Which organization publishes {title}?")

     if alias:
        questions.append(f"Who is known as {title}?")

     if years:
        questions.append(f"When was {title} first introduced?")

     questions.append(f"Explain the importance of {title}.")
     questions.append(f"Write short notes on {title}.")

     questions = questions[:6]

    # ================= QUICK REVISION =================

     revision = "\n".join(
        f"• {point}" for point in key_points[:5]
    )

    # ================= READING STATS =================

     word_count = len(article.split())
     reading_time = max(1, word_count // 200)

    # ================= CONCEPT MAP =================

     concept_map = self.generate_concept_map(title, article)

    # ================= RETURN =================

     return {

        "title": title,

        "overview": overview,

        "key_points": key_points,

        "keywords": keywords,

        "facts": facts,
        "did_you_know": did_you_know,

        "questions": questions,

        "revision": revision,

        "concept_map": concept_map,

        "reading_time": reading_time,

        "word_count": word_count
        
    }
         
    def generate_concept_map(self, title, article):

     creator = "Unknown"
     publisher = "Unknown"
     alias = "Unknown"
     year = "Unknown"

     m = re.search(r"created by ([^.]+)", article, re.IGNORECASE)
     if m:
        creator = m.group(1).split(",")[0].replace("writer","").replace("artist","").strip()

     m = re.search(r"published by ([^.]+)", article, re.IGNORECASE)
     if m:
        publisher = m.group(1).split(",")[0].strip()

     m = re.search(r"alias of ([^.]+)", article, re.IGNORECASE)
     if m:
        alias = m.group(1).split(",")[0].strip()

     if alias == "Unknown":

        m = re.search(
            r"secret identity of ([^.]+)",
            article,
            re.IGNORECASE
        )

        if m:
            alias = m.group(1).split(",")[0].strip()

     m = re.search(r"\b(19\d{2}|20\d{2})\b", article)

     if m:
        year = m.group()

     concept = f"""
CONCEPT MAP

                 {title}
                    │
      ┌─────────────┼─────────────┐
      │             │             │
   Creator      Publisher      Alias
      │             │             │
  {creator}    {publisher}     {alias}
                    │
               First Appeared
                    │
                  {year}
"""

     return concept