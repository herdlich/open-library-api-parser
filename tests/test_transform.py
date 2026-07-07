from open_library_parser.transform import transform_items


def test_transform_full_book():
    raw_data = {
        "docs": [
            {
                "key": "/works/OL123W",
                "title": "Python Basics",
                "author_name": ["Alice", "Bob"],
                "first_publish_year": 2020,
                "language": ["eng", "deu"],
                "edition_count": 4,
                "cover_i": 12345,
                "ia": ["book1", "book2", "book3", "book4"]
            }
        ]
    }

    result = transform_items(raw_data)

    assert len(result) == 1

    book = result[0]

    assert book["book_id"] == "OL123W"
    assert book["title"] == "Python Basics"
    assert book["author_name"] == "Alice, Bob"
    assert book["language"] == "eng, deu"
    assert book["first_publish_year"] == 2020
    assert book["edition_count"] == 4
    assert book["cover_i"] == 12345
    assert book["cover_link"] == "https://covers.openlibrary.org/b/id/12345-L.jpg"
    assert book["ia"] == "book1, book2, book3"
    assert book["link"] == "https://openlibrary.org/works/OL123W"


def test_incomplete_book_data():
    raw_data = {
        "docs": [
            {
                "key": "/works/OL123W"
            }
        ]
    }

    result = transform_items(raw_data)

    assert len(result) == 1

    book = result[0]

    assert book["book_id"] == "OL123W"
    assert book["title"] == ""
    assert book["author_name"] == ""
    assert book["first_publish_year"] is None
    assert book["language"] == ""
    assert book["edition_count"] is None
    assert book["cover_i"] is None
    assert book["ia"] == ""


def test_no_book_key_skip():
    raw_data = {
        "docs": [
            {
                "title": "Python Basics",
                "author_name": ["Alice", "Bob"],
                "first_publish_year": 2020,
                "language": ["eng", "deu"],
                "edition_count": 4,
                "cover_i": 12345,
                "ia": ["book1", "book2", "book3", "book4"]
            }
        ]
    }

    result = transform_items(raw_data)

    assert result == []


def test_no_data():
    raw_data = {}

    result = transform_items(raw_data)

    assert result == []


def test_empty_docs():
    raw_data = {"docs": []}

    result = transform_items(raw_data)

    assert result == []
