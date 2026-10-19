import pytest

from app import VocabularyStore


def test_add_entry_strips_text_and_defaults_to_learning(tmp_path):
    store = VocabularyStore(tmp_path / "vocabulary.sqlite3")

    entry = store.add_entry(
        {
            "kanji": " 食べる ",
            "reading": " たべる ",
            "meaning": " to eat ",
            "partOfSpeech": " verb ",
        }
    )

    assert entry["kanji"] == "食べる"
    assert entry["reading"] == "たべる"
    assert entry["meaning"] == "to eat"
    assert entry["partOfSpeech"] == "verb"
    assert entry["status"] == "learning"


@pytest.mark.parametrize("status", ["known", "learning", "please review"])
def test_add_entry_accepts_each_learning_status(tmp_path, status):
    store = VocabularyStore(tmp_path / "vocabulary.sqlite3")

    entry = store.add_entry(
        {
            "kanji": "猫",
            "reading": "ねこ",
            "meaning": "cat",
            "partOfSpeech": "noun",
            "status": status,
        }
    )

    assert entry["status"] == status


def test_add_entry_rejects_missing_or_blank_required_fields(tmp_path):
    store = VocabularyStore(tmp_path / "vocabulary.sqlite3")

    with pytest.raises(ValueError, match="required"):
        store.add_entry(
            {"kanji": "犬", "reading": "いぬ", "meaning": " ", "partOfSpeech": "noun"}
        )


def test_add_entry_rejects_unknown_status(tmp_path):
    store = VocabularyStore(tmp_path / "vocabulary.sqlite3")

    with pytest.raises(ValueError, match="status"):
        store.add_entry(
            {
                "kanji": "犬",
                "reading": "いぬ",
                "meaning": "dog",
                "partOfSpeech": "noun",
                "status": "mastered",
            }
        )


def test_list_entries_returns_newest_entry_first(tmp_path):
    store = VocabularyStore(tmp_path / "vocabulary.sqlite3")
    store.add_entry({"kanji": "春", "reading": "はる", "meaning": "spring", "partOfSpeech": "noun"})
    newest = store.add_entry({"kanji": "夏", "reading": "なつ", "meaning": "summer", "partOfSpeech": "noun"})

    entries = store.list_entries()

    assert entries[0]["id"] == newest["id"]
    assert entries[0]["kanji"] == "夏"