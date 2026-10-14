import re


class IntentEngine:

    def detect(self, query):

        q = query.lower()

        # ---------- NOTES ----------

        if any(word in q for word in [
            "note",
            "notes",
            "study",
            "summary",
            "summarize"
        ]):
            intent = "notes"

        # ---------- QUIZ ----------

        elif any(word in q for word in [
            "quiz",
            "mcq",
            "test",
            "question"
        ]):
            intent = "quiz"

        # ---------- IMAGE ----------

        elif any(word in q for word in [
            "image",
            "picture",
            "photo",
            "diagram"
        ]):
            intent = "image"

        # ---------- COMPARE ----------

        elif any(word in q for word in [
            "compare",
            "difference",
            "vs",
            "versus"
        ]):
            intent = "compare"

        # ---------- SAVE ----------

        elif any(word in q for word in [
            "save",
            "bookmark"
        ]):
            intent = "save"

        else:
            intent = "ai"

        # -------- Extract Topic --------

        stop_words = {
            "what","who","why","when","where","is","are","the","a","an",
            "of","to","for","tell","about","explain","make","generate",
            "create","show","image","picture","photo","notes","note",
            "quiz","summary","summarize","save","compare","difference",
            "between","me","on"
        }

        words = re.findall(r"[A-Za-z0-9\-\+]+", query)

        topic = []

        for word in words:

            if word.lower() not in stop_words:

                topic.append(word)

        topic = " ".join(topic)

        return intent, topic