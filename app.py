import json
import os
import sqlite3
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).parent
DEFAULT_DATABASE = ROOT / "vocabulary.sqlite3"
VALID_STATUSES = {"known", "learning", "please review"}


class VocabularyStore:
    def __init__(self, database_path=DEFAULT_DATABASE):
        self.database_path = str(database_path)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kanji TEXT NOT NULL,
                    reading TEXT NOT NULL,
                    meaning TEXT NOT NULL,
                    part_of_speech TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'learning',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _connect(self):
        return sqlite3.connect(self.database_path)

    def list_entries(self):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, kanji, reading, meaning, part_of_speech, status, created_at
                FROM vocabulary
                ORDER BY id DESC
                """
            ).fetchall()
        return [
            {
                "id": row[0],
                "kanji": row[1],
                "reading": row[2],
                "meaning": row[3],
                "partOfSpeech": row[4],
                "status": row[5],
                "createdAt": row[6],
            }
            for row in rows
        ]

    def add_entry(self, entry):
        required_fields = ("kanji", "reading", "meaning", "partOfSpeech")
        if any(not isinstance(entry.get(field), str) or not entry[field].strip() for field in required_fields):
            raise ValueError("kanji, reading, meaning, and partOfSpeech are required")
        status = entry.get("status", "learning")
        if status not in VALID_STATUSES:
            raise ValueError("status must be known, learning, or please review")

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO vocabulary (kanji, reading, meaning, part_of_speech, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                tuple(entry[field].strip() for field in required_fields) + (status,),
            )
            entry_id = cursor.lastrowid
        return next(item for item in self.list_entries() if item["id"] == entry_id)


class VocabularyHandler(SimpleHTTPRequestHandler):
    store = None

    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=str(directory or ROOT / "static"), **kwargs)

    def do_GET(self):
        if urlparse(self.path).path == "/api/vocabulary":
            self._send_json(HTTPStatus.OK, self.store.list_entries())
            return
        super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/vocabulary":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            created = self.store.add_entry(payload)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
            return
        self._send_json(HTTPStatus.CREATED, created)

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        return


def create_server(address=("127.0.0.1", 8000), database_path=DEFAULT_DATABASE):
    VocabularyHandler.store = VocabularyStore(database_path)
    return ThreadingHTTPServer(address, VocabularyHandler)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    server = create_server(("0.0.0.0", port), os.environ.get("DATABASE_PATH", DEFAULT_DATABASE))
    print(f"Vocabulary tracker running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()