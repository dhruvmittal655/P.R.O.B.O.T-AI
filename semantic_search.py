from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import re
import threading


class SemanticSearch:

    def __init__(self):

        self.model = None
        self._model_lock = threading.Lock()

    def load_model(self):
        """Load the embedding model once, on demand."""

        if self.model is not None:
            return self.model

        with self._model_lock:
            if self.model is not None:
                return self.model

            try:
                print("Trying local model...")
                self.model = SentenceTransformer(
                    "all-MiniLM-L6-v2",
                    local_files_only=True
                )
                print("Local model loaded.")
            except Exception:
                print("Downloading model...")
                self.model = SentenceTransformer("all-MiniLM-L6-v2")

        return self.model

    # -------------------------------------------------

    def top_matches(self, query, titles, top_k=5, threshold=0.55):

        if not titles:
            return []

        model = self.load_model()

        query_embedding = model.encode(
            query,
            convert_to_tensor=True
        )

        title_embeddings = model.encode(
            titles,
            convert_to_tensor=True
        )

        scores = cos_sim(
            query_embedding,
            title_embeddings
        )[0]

        results = []

        for i, score in enumerate(scores):

            score = score.item()

            if score >= threshold:

                results.append(
                    (titles[i], score)
                )

        results.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return results[:top_k]

    # -------------------------------------------------

    def retrieve_context(
        self,
        article,
        question,
        top_k=10,
        min_score=0.10
    ):
        if not article:
            return ""

        # ------------------------
        # NORMAL ARTICLE
        # ------------------------
        if isinstance(article, str):
            # For documents/articles under 5000 chars, return full text to ensure 100% accuracy for names, roll nos, & metadata
            if len(article.strip()) <= 5000:
                return article.strip()

            raw_units = re.split(r'\n+|(?:(?<=[.!?])\s+)', article)
            sentences = [
                u.strip()
                for u in raw_units
                if len(u.strip()) >= 3
            ]
        else:
            sentences = article

        if len(sentences) == 0:
            return article if isinstance(article, str) else ""

        model = self.load_model()

        question_embedding = model.encode(
            question,
            convert_to_tensor=True
        )

        sentence_embeddings = model.encode(
            sentences,
            convert_to_tensor=True
        )

        scores = cos_sim(
            question_embedding,
            sentence_embeddings
        )[0]

        ranked = []
        for index, score in enumerate(scores):
            ranked.append((index, score.item()))

        ranked.sort(key=lambda x: x[1], reverse=True)

        selected = []
        for index, score in ranked:
            if score < min_score and len(selected) > 0:
                continue

            selected.append(sentences[index])

            if len(selected) >= top_k:
                break

        if not selected and isinstance(article, str):
            return article[:5000]

        return "\n\n".join(selected)
    def best_matching_title(self, titles, question):

     if not titles:
        return None

     model = self.load_model()

     title_embeddings = model.encode(
        titles,
        convert_to_tensor=True
    )

     question_embedding = model.encode(
        question,
        convert_to_tensor=True
    )

     scores = cos_sim(
        question_embedding,
        title_embeddings
    )[0]

     best_index = scores.argmax().item()

     best_score = scores[best_index].item()

     if best_score < 0.40:
        return None

     return titles[best_index]
