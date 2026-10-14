import sqlite3
import os
from datetime import datetime


class Database:

    def __init__(self, database_path=None):
        if database_path is None:
            project_folder = os.path.dirname(os.path.abspath(__file__))
            data_folder = os.path.join(project_folder, "data")
            os.makedirs(data_folder, exist_ok=True)
            database_path = os.path.join(data_folder, "knowledge.db")

        self.database_path = database_path
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        import threading
        self.lock = threading.Lock()

        try:
            self.cursor.execute("PRAGMA journal_mode=WAL")
            self.cursor.execute("PRAGMA synchronous=NORMAL")
            self.connection.commit()
        except Exception:
            pass

        self.create_table()
        self.create_research_chunks_table()
        self.create_research_table()
        self.migrate_schema()
        self.create_indexes()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            summary TEXT,
            image_path TEXT,
            date_saved TEXT,
            last_opened TEXT,
            views INTEGER DEFAULT 0,
            favorite INTEGER DEFAULT 0
        )
        """)
        self.connection.commit()

    def migrate_schema(self):
        required_article_columns = {
            "image_path": "TEXT",
            "date_saved": "TEXT",
            "last_opened": "TEXT",
            "views": "INTEGER DEFAULT 0",
            "favorite": "INTEGER DEFAULT 0",
        }

        self.cursor.execute("PRAGMA table_info(articles)")
        existing_columns = {row[1] for row in self.cursor.fetchall()}
        for column, definition in required_article_columns.items():
            if column not in existing_columns:
                self.cursor.execute(f"ALTER TABLE articles ADD COLUMN {column} {definition}")

        self.connection.commit()

    def create_indexes(self):
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_chunks_topic ON research_chunks(topic)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_sources_topic ON research_sources(topic)")
        self.connection.commit()

    def save_article(self, title, summary, image_path="", date_saved=None, last_opened=None):
        if date_saved is None:
            date_saved = datetime.now().strftime("%Y-%m-%d")
        if last_opened is None:
            last_opened = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("""
        INSERT OR IGNORE INTO articles (title, summary, image_path, date_saved, last_opened, views, favorite)
        VALUES (?, ?, ?, ?, ?, 1, 0)
        """, (title, summary, image_path, date_saved, last_opened))
        self.connection.commit()

    def save_or_update_article(self, title, summary, image_path="", date_saved=None, last_opened=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.article_exists(title):
            self.cursor.execute("""
                UPDATE articles
                SET summary=?, last_opened=?, views = views + 1
                WHERE title=?
            """, (summary, now, title))
            self.connection.commit()
        else:
            self.save_article(title, summary, image_path, date_saved, now)

    def get_article(self, title):
        self.cursor.execute("SELECT * FROM articles WHERE title=?", (title,))
        return self.cursor.fetchone()

    def get_image_path(self, title):
        self.cursor.execute("SELECT image_path FROM articles WHERE title=?", (title,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def update_image_path(self, title, image_path):
        self.cursor.execute("UPDATE articles SET image_path=? WHERE title=?", (image_path, title))
        self.connection.commit()

    def article_exists(self, title):
        self.cursor.execute("SELECT 1 FROM articles WHERE title=?", (title,))
        return self.cursor.fetchone() is not None

    def update_views(self, title):
        self.cursor.execute("UPDATE articles SET views = views + 1 WHERE title=?", (title,))
        self.connection.commit()

    def update_last_opened(self, title):
        current = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("UPDATE articles SET last_opened=? WHERE title=?", (current, title))
        self.connection.commit()

    def add_favorite(self, title):
        self.cursor.execute("UPDATE articles SET favorite=1 WHERE title=?", (title,))
        self.connection.commit()

    def remove_favorite(self, title):
        self.cursor.execute("UPDATE articles SET favorite=0 WHERE title=?", (title,))
        self.connection.commit()

    def get_favorites(self):
        self.cursor.execute("SELECT title FROM articles WHERE favorite=1 ORDER BY title")
        return self.cursor.fetchall()

    def get_most_viewed(self, limit=10):
        self.cursor.execute("SELECT title, views FROM articles ORDER BY views DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def search_titles(self, keyword):
        self.cursor.execute("SELECT title FROM articles WHERE title LIKE ? LIMIT 5", (f"%{keyword}%",))
        return self.cursor.fetchall()

    def total_articles(self):
        self.cursor.execute("SELECT COUNT(*) FROM articles")
        return self.cursor.fetchone()[0]

    def total_favorites(self):
        self.cursor.execute("SELECT COUNT(*) FROM articles WHERE favorite=1")
        return self.cursor.fetchone()[0]

    def total_views(self):
        self.cursor.execute("SELECT SUM(views) FROM articles")
        result = self.cursor.fetchone()[0]
        return result if result is not None else 0

    def delete_article(self, title):
        self.cursor.execute("DELETE FROM articles WHERE title=?", (title,))
        self.cursor.execute("DELETE FROM research_sources WHERE topic=?", (title,))
        self.cursor.execute("DELETE FROM research_chunks WHERE topic=?", (title,))
        self.connection.commit()

    def get_history(self, limit=None):
        if limit is None:
            self.cursor.execute("SELECT title, last_opened, views FROM articles ORDER BY last_opened DESC")
        else:
            self.cursor.execute("SELECT title, last_opened, views FROM articles ORDER BY last_opened DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def clear_history(self):
        self.cursor.execute("DELETE FROM articles")
        self.connection.commit()

    def clear_all_database_data(self):
        self.cursor.execute("DELETE FROM articles")
        self.cursor.execute("DELETE FROM research_sources")
        self.cursor.execute("DELETE FROM research_chunks")
        self.connection.commit()

    def close(self):
        self.connection.close()

    def get_all_titles(self):
        self.cursor.execute("SELECT title FROM articles")
        results = self.cursor.fetchall()
        return [row[0] for row in results]

    def get_summary(self, title):
        row = self.get_article(title)
        return row[2] if row else None

    def create_research_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_sources(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            source_name TEXT,
            source_url TEXT,
            content TEXT,
            downloaded_on TEXT
        )
        """)
        self.connection.commit()

    def save_research_source(self, topic, source_name, source_url, content, downloaded_on):
        self.cursor.execute("""
            DELETE FROM research_sources WHERE topic=? AND source_name=? AND source_url=?
        """, (topic, source_name, source_url))
        self.cursor.execute("""
            INSERT INTO research_sources (topic, source_name, source_url, content, downloaded_on)
            VALUES (?, ?, ?, ?, ?)
        """, (topic, source_name, source_url, content, downloaded_on))
        self.connection.commit()

    def get_references_for_topic(self, topic):
        self.cursor.execute("""
            SELECT source_name, source_url, downloaded_on
            FROM research_sources
            WHERE topic=? AND source_name IN ('arXiv Papers', 'OpenAlex Literature', 'PubMed Central', 'Semantic Scholar')
            ORDER BY id
        """, (topic,))
        return self.cursor.fetchall()

    def get_research_sources(self, topic):
        self.cursor.execute("""
            SELECT source_name, source_url, content
            FROM research_sources
            WHERE topic=? AND source_name IN ('arXiv Papers', 'OpenAlex Literature', 'PubMed Central', 'Semantic Scholar')
            ORDER BY id
        """, (topic,))
        return self.cursor.fetchall()

    def create_research_chunks_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_chunks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                source_name TEXT,
                source_url TEXT,
                chunk TEXT
            )
        """)
        self.connection.commit()

    def save_chunk(self, topic, source_name, source_url, chunk):
        self.cursor.execute(
            "INSERT INTO research_chunks(topic, source_name, source_url, chunk) VALUES(?,?,?,?)",
            (topic, source_name, source_url, chunk)
        )
        self.connection.commit()

    def get_chunks(self, topic):
        self.cursor.execute("SELECT chunk, source_name FROM research_chunks WHERE topic=?", (topic,))
        return self.cursor.fetchall()

    def get_full_research(self, topic):
        self.cursor.execute("SELECT chunk FROM research_chunks WHERE topic=? ORDER BY id", (topic,))
        rows = self.cursor.fetchall()
        return "\n\n".join(row[0] for row in rows)

    def research_pack_exists(self, topic):
        self.cursor.execute("SELECT COUNT(*) FROM research_chunks WHERE topic=?", (topic,))
        return self.cursor.fetchone()[0] > 0

    def delete_research_pack(self, topic):
        self.cursor.execute("DELETE FROM research_chunks WHERE topic=?", (topic,))
        self.cursor.execute("DELETE FROM research_sources WHERE topic=?", (topic,))
        self.connection.commit()

    def get_all_articles_summaries_threadsafe(self):
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT title, summary FROM articles")
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def get_all_research_chunks_threadsafe(self):
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT topic, chunk FROM research_chunks")
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []
