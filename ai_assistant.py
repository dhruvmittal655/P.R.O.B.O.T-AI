import ollama
import spacy
import re
from semantic_search import SemanticSearch
import time
import threading


class SmartAIAssistant:

    def __init__(self, database):
        self.database = database
        self.nlp = None
        self._nlp_lock = threading.Lock()
        self.semantic = SemanticSearch()
        self.chat_history = []
        self.current_topic = None
        self.current_article = None

    def set_article(self, topic, article):
        """Set the active article."""
        self.current_topic = topic
        self.current_article = article

    def get_best_model(self):
        """Auto-detect highest quality installed Ollama model with caching to eliminate HTTP lookup latency."""
        if hasattr(self, "_cached_model") and self._cached_model:
            return self._cached_model

        try:
            models_info = ollama.list().get("models", [])
            names = [m.get("name") or m.get("model") or "" for m in models_info]
            for preferred in ["llama3:8b", "llama3:latest", "llama3", "mistral:latest", "mistral", "qwen2.5", "phi3:mini"]:
                for name in names:
                    if preferred in name.lower():
                        self._cached_model = name
                        return name
        except Exception:
            pass
        self._cached_model = "phi3:mini"
        return "phi3:mini"

    def load_nlp(self):
        """Load SpaCy's language model only when topic extraction needs it."""
        if self.nlp is not None:
            return self.nlp

        with self._nlp_lock:
            if self.nlp is None:
                self.nlp = spacy.load("en_core_web_sm")

        return self.nlp

    def auto_search(self, question):
        titles = self.database.get_all_titles()
        title = self.semantic.best_matching_title(titles, question)

        if not title:
            return False

        article = self.database.get_article(title)
        if article:
            self.set_article(title, article[2])
            return True

        return False

    def extract_topic(self, question):
        doc = self.load_nlp()(question)

        if len(doc.ents) > 0:
            return doc.ents[0].text

        stop_words = {
            "what", "who", "when", "where", "why", "how",
            "is", "are", "was", "were", "the", "a", "an",
            "about", "tell", "me", "explain", "describe",
            "give", "information", "on"
        }

        words = []
        for token in doc:
            if (
                token.text.lower() not in stop_words
                and token.is_alpha
            ):
                words.append(token.text)

        return " ".join(words)

    def _build_prompt(self, context, history, question):
        return f"""You are SmartSearch AI, an intelligent research assistant.

Your goal is to provide a clear, comprehensive, and well-structured answer based ON ONLY the provided research context.

Formatting & Structure Guidelines:
1. **Direct Answer / Summary**: Begin with a clear 2-sentence direct summary answer.
2. **Detailed Breakdown**: Use structured bullet points, bold key terms, and clear sections to explain the concepts thoroughly.
3. **Accuracy**: Base your response strictly on facts present in the research context.
4. **Source Attribution**: Mention which document/topic the information comes from.
5. **Clarity**: Be professional, educational, and engaging.

========================
RESEARCH CONTEXT
========================
{context}

========================
CONVERSATION HISTORY
========================
{history}

========================
USER QUESTION
========================
{question}

========================
AI RESPONSE
========================
"""

    def get_scoped_rag_context(self, question, scope="current"):
        """Retrieve grounded RAG context according to scope: current open file vs global research library."""
        if scope == "global":
            global_texts = []

            chunks = self.database.get_all_research_chunks_threadsafe()
            for topic, chunk in chunks:
                if chunk and len(chunk.strip()) > 30:
                    global_texts.append(f"[{topic}] {chunk.strip()}")

            articles = self.database.get_all_articles_summaries_threadsafe()
            for title, summary in articles:
                if summary and len(summary.strip()) > 30:
                    global_texts.append(f"[{title}] {summary.strip()}")

            if global_texts:
                context = self.semantic.retrieve_context(global_texts, question, top_k=15, min_score=0.18)
                if context:
                    return context

        if not self.current_article and self.current_topic:
            row = self.database.get_article(self.current_topic)
            if row and len(row) > 2 and row[2]:
                self.current_article = row[2]

        if self.current_article:
            return self.semantic.retrieve_context(self.current_article, question, top_k=12)

        return ""

    def ask(self, article, question, scope="current"):
        context = self.get_scoped_rag_context(question, scope=scope)
        if context == "":
            return "I couldn't find relevant information in the selected scope.", 0

        context = context.strip().replace("\n\n\n", "\n\n")
        history = ""
        for role, message in self.chat_history[-6:]:
            history += f"{role}: {message}\n"

        prompt = self._build_prompt(context, history, question)
        model_name = self.get_best_model()

        start = time.time()
        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3, "top_p": 0.9, "repeat_penalty": 1.15, "num_gpu": 99}
        )
        elapsed = time.time() - start
        answer = response["message"]["content"]

        self.chat_history.append(("User", question))
        self.chat_history.append(("AI", answer))
        return answer, elapsed

    def stream_ask(self, article, question, scope="current"):
        context = self.get_scoped_rag_context(question, scope=scope)
        if context == "":
            yield "I couldn't find relevant information in the selected scope."
            return

        context = context.strip().replace("\n\n\n", "\n\n")
        history = ""
        for role, message in self.chat_history[-6:]:
            history += f"{role}: {message}\n"

        prompt = self._build_prompt(context, history, question)
        model_name = self.get_best_model()

        full_answer = ""
        try:
            stream = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3, "top_p": 0.9, "repeat_penalty": 1.15, "num_gpu": 99},
                stream=True
            )
            for chunk in stream:
                token = chunk.get("message", {}).get("content", "")
                if token:
                    full_answer += token
                    yield token
        except Exception as e:
            err = f"AI Error: {e}"
            full_answer = err
            yield err

        if full_answer:
            self.chat_history.append(("User", question))
            self.chat_history.append(("AI", full_answer))

    def update_topic(self, topic, database, downloader):
        if not topic:
            return False

        topic = topic.strip()
        if not topic:
            return False

        if (
            self.current_topic
            and self.current_article
            and topic.lower() == self.current_topic.lower()
        ):
            return True

        article = None
        if database.article_exists(topic):
            row = database.get_article(topic)
            if row:
                article = row[2]
        else:
            article = downloader.get_summary(topic)
            if article:
                database.save_article(topic, article)

        if not article:
            return False

        self.set_article(topic, article)
        return True
