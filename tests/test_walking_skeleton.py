import json
import threading
from http.client import HTTPConnection

from app import create_server


def request(server, method, path, body=None):
    connection = HTTPConnection(*server.server_address)
    headers = {"Content-Type": "application/json"} if body else {}
    connection.request(method, path, body=json.dumps(body) if body else None, headers=headers)
    response = connection.getresponse()
    payload = json.loads(response.read())
    connection.close()
    return response.status, payload


def test_vocabulary_survives_a_real_http_round_trip(tmp_path):
    database = tmp_path / "vocabulary.sqlite3"
    server = create_server(("127.0.0.1", 0), database)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, created = request(
            server,
            "POST",
            "/api/vocabulary",
            {"kanji": "食べる", "reading": "たべる", "meaning": "to eat", "partOfSpeech": "verb"},
        )
        assert status == 201
        assert created["status"] == "learning"

        server.shutdown()
        thread.join()
        server.server_close()

        reopened_server = create_server(("127.0.0.1", 0), database)
        reopened_thread = threading.Thread(target=reopened_server.serve_forever, daemon=True)
        reopened_thread.start()
        try:
            status, entries = request(reopened_server, "GET", "/api/vocabulary")
            assert status == 200
            assert entries[0]["meaning"] == "to eat"
            assert entries[0]["kanji"] == "食べる"
        finally:
            reopened_server.shutdown()
            reopened_thread.join()
            reopened_server.server_close()
    finally:
        if thread.is_alive():
            server.shutdown()
            thread.join()
            server.server_close()