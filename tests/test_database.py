import sqlite3
from open_library_parser.database import db_init, save_to_db


def make_book(edition_count=4):
    return {
        "book_id": "OL123W",
        "title": "Python Basics",
        "author_name": "Alice",
        "first_publish_year": 2020,
        "language": "eng",
        "edition_count": edition_count,
        "cover_i": 12345,
        "cover_link": "https://covers.openlibrary.org/b/id/12345-L.jpg",
        "ia": "book1",
        "link": "https://openlibrary.org/works/OL123W",
    }


def test_db_init_creates_books_table(tmp_path):
    db_file = tmp_path / "data" / "books.db"

    db_init(db_file)

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = 'books'
    """)

    table = cursor.fetchone()
    connection.close()

    assert table is not None


def test_save_to_db_adds_books(tmp_path):
    db_file = tmp_path / "data" / "books.db"

    db_init(db_file)
    save_to_db(db_file, [make_book()])

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT title, edition_count FROM books WHERE book_id = ?",
        ("OL123W",),
    )

    row = cursor.fetchone()
    connection.close()

    assert row is not None
    assert row[0] == "Python Basics"
    assert row[1] == 4


def test_save_to_db_updates_existing_book(tmp_path):
    db_file = tmp_path / "data" / "books.db"

    db_init(db_file)

    save_to_db(db_file, [make_book(edition_count=4)])
    save_to_db(db_file, [make_book(edition_count=10)])

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*), edition_count
        FROM books
        WHERE book_id = ?
        """,
        ("OL123W",)
    )

    count, edition_count = cursor.fetchone()
    connection.close()

    assert count == 1
    assert edition_count == 10
