import sqlite3
from pathlib import Path


def db_init(db_file):
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id TEXT PRIMARY KEY,
        title TEXT,
        author_name TEXT,
        first_publish_year INTEGER,
        language TEXT,
        edition_count INTEGER,
        cover_i INTEGER,
        cover_link TEXT,
        ia TEXT,
        link TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_to_db(db_file, items):
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    rows = [
        (
            item["book_id"],
            item["title"],
            item["author_name"],
            item["first_publish_year"],
            item["language"],
            item["edition_count"],
            item["cover_i"],
            item["cover_link"],
            item["ia"],
            item["link"],
        )
        for item in items
    ]

    cursor.executemany("""
    INSERT INTO books (book_id, title, author_name, first_publish_year, language, 
    edition_count, cover_i, cover_link, ia, link)
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(book_id) DO UPDATE SET
    title = excluded.title,
    author_name = excluded.author_name,
    first_publish_year = excluded.first_publish_year,
    language = excluded.language,
    edition_count = excluded.edition_count,
    cover_i = excluded.cover_i,
    cover_link = excluded.cover_link,
    ia = excluded.ia,
    link = excluded.link
    """, rows)

    connection.commit()
    connection.close()
