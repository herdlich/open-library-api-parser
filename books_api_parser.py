import csv
import time
import requests
import argparse
import logging
import sqlite3
from urllib.parse import urljoin
from pathlib import Path

API_URL = "https://openlibrary.org/search.json"
BOOK_URL = "https://openlibrary.org"

Path("logs").mkdir(exist_ok=True)
time_format = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(filename="logs/books_parser.log", level=logging.INFO, encoding="utf-8",
                    format="[%(asctime)s] - %(levelname)s: %(message)s", datefmt=time_format)


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--output", default="data/books.csv")
    parser.add_argument("--db", default="data/books.db")
    parser.add_argument("--query", default="python")
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--limit", type=int, default=50)

    return parser.parse_args()


def fetch_data(query, page, limit):
    params = {
        "q": query,
        "page": page,
        "limit": limit
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as error:
        print(f"Request error: {error}")
        logging.error(f"Request error: {error}")

        return None


def transform_items(data):
    books_list = []

    if data and "docs" in data:
        for doc in data["docs"]:
            title = doc.get("title") or ""

            author_list = doc.get("author_name") or []
            author_name = ", ".join(author_list) if isinstance(author_list, list) else str(author_list)

            language_list = doc.get("language") or []
            language = ", ".join(language_list) if isinstance(language_list, list) else str(language_list)

            first_publish_year = doc.get("first_publish_year")

            work_key = doc.get("key")
            if not work_key:
                logging.warning("Work key not found. SKIP book")
                continue

            link = urljoin(BOOK_URL, work_key)

            book_id = work_key.split("/")[-1]
            if not book_id:
                logging.warning("Book ID not found. SKIP book")
                continue

            edition_count = doc.get("edition_count")

            cover_i = doc.get("cover_i")

            ia_list = doc.get("ia") or []
            ia = ", ".join(map(str, ia_list[:3])) if isinstance(ia_list, list) else str(ia_list)

            cover_link = f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg" if cover_i else ""

            book_dict = {
                "book_id": book_id,
                "title": title,
                "author_name": author_name,
                "first_publish_year": first_publish_year,
                "language": language,
                "edition_count": edition_count,
                "cover_i": cover_i,
                "cover_link": cover_link,
                "ia": ia,
                "link": link,
            }

            books_list.append(book_dict)

    return books_list


def parse_all_pages(pages, query, limit):
    all_books = []

    for page in range(1, pages + 1):
        raw_items = fetch_data(query, page, limit)
        if raw_items is None:
            logging.warning(f"API request failed on page {page}. STOP")
            break

        clean_items = transform_items(raw_items)
        if not clean_items:
            logging.warning("Cleanup was unsuccessful. STOP")
            break

        all_books.extend(clean_items)

        logging.info(f"Parsed page: {page}, books found: {len(clean_items)}")

        time.sleep(0.5)

    return all_books


def save_csv(csv_file, csv_data):
    Path(csv_file).parent.mkdir(parents=True, exist_ok=True)

    with open(csv_file, "w", encoding="utf-8", newline="") as file:
        fieldnames = ["book_id", "title", "author_name", "first_publish_year", "language", "edition_count", "cover_i",
                      "cover_link", "ia", "link"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(csv_data)


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


def main():
    args = get_args()

    db_init(args.db)

    all_books = parse_all_pages(args.pages, args.query, args.limit)
    if not all_books:
        print("No books found")
        logging.warning("No books found. STOP")
        return

    save_csv(args.output, all_books)
    save_to_db(args.db, all_books)

    print(f"Books saved: {len(all_books)}")
    print(f"Output: {args.output}")
    print(f"Database: {args.db}")

    logging.info(f"Books saved: {len(all_books)}")
    logging.info(f"Output: {args.output}")
    logging.info(f"Database: {args.db}")


if __name__ == "__main__":
    main()
