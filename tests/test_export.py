import csv
from open_library_parser.export import save_csv


def test_save_csv_creates_file(tmp_path):
    csv_file = tmp_path / "data" / "books.csv"

    books = [
        {
            "book_id": "OL123W",
            "title": "Python Basics",
            "author_name": "Alice",
            "first_publish_year": 2020,
            "language": "eng",
            "edition_count": 4,
            "cover_i": 12345,
            "cover_link": "https://covers.openlibrary.org/b/id/12345-L.jpg",
            "ia": "book1",
            "link": "https://openlibrary.org/works/OL123W",
        }
    ]

    save_csv(csv_file, books)

    assert csv_file.exists()

    with open(csv_file, encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["book_id"] == "OL123W"
    assert rows[0]["title"] == "Python Basics"


def test_save_csv_has_correct_headers(tmp_path):
    csv_file = tmp_path / "data" / "books.csv"

    books = [
        {
            "book_id": "OL123W",
            "title": "Python Basics",
            "author_name": "Alice",
            "first_publish_year": 2020,
            "language": "eng",
            "edition_count": 4,
            "cover_i": 12345,
            "cover_link": "https://covers.openlibrary.org/b/id/12345-L.jpg",
            "ia": "book1",
            "link": "https://openlibrary.org/works/OL123W",
        }
    ]

    save_csv(csv_file, books)

    with open(csv_file, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames

    expected_headers = [
        "book_id",
        "title",
        "author_name",
        "first_publish_year",
        "language",
        "edition_count",
        "cover_i",
        "cover_link",
        "ia",
        "link"
    ]

    assert headers == expected_headers
