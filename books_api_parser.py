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

    return parser.parse_args()


def fetch_data(query, page):
    params = {
        "q": query,
        "page": page,
        "limit": 50
    }

    try:
        response = requests.get(API_URL, params=params, timeout=10)

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as error:
        print(f"Request error: {error}")
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

            first_publish_year = doc.get("first_publish_year") or ""

            work_key = doc.get("key")
            link = urljoin(BOOK_URL, work_key) if work_key else None

            book_id = work_key.split("/")[-1] if work_key else ""

            book_dict = {
                "title": title,
                "author_name": author_name,
                "language": language,
                "first_publish_year": first_publish_year,
                "link": link,
                "book_id": book_id
            }

            books_list.append(book_dict)

    return books_list


def parse_all_pages(pages, query):
    all_books = []

    for page in range(1, pages + 1):
        raw_items = fetch_data(query, page)
        if not raw_items:
            continue

        clean_items = transform_items(raw_items)
        if not clean_items:
            continue

        all_books.extend(clean_items)

        time.sleep(0.5)

    if not all_books:
        return None

    return all_books


def save_csv(csv_file, csv_data):
    Path(csv_file).parent.mkdir(parents=True, exist_ok=True)

    with open(csv_file, "w", encoding="utf-8", newline="") as file:
        fieldnames = ["title", "author_name", "language", "first_publish_year", "link", "book_id"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(csv_data)


def db_init(db_file):
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        title TEXT,
        author_name TEXT,
        language TEXT,
        first_publish_year INTEGER,
        link TEXT,
        book_id TEXT PRIMARY KEY
        )
    """)

    connection.commit()
    connection.close()


def save_to_db(db_file, items):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.executemany("""
    INSERT OR IGNORE INTO books (title, author_name, language, first_publish_year, link, book_id)
    VALUES(?, ?, ?, ?, ?, ?)
    """, [
        (
            item["title"],
            item["author_name"],
            item["language"],
            item["first_publish_year"] if item["first_publish_year"] else None,
            item["link"],
            item["book_id"]
        )
        for item in items
    ])

    connection.commit()
    connection.close()


def main():
    args = get_args()

    db_init(args.db)

    all_books = parse_all_pages(args.pages, args.query)
    if not all_books:
        print("No books found")
        logging.warning("No books found")
        return

    save_csv(args.output, all_books)
    save_to_db(args.db, all_books)


if __name__ == "__main__":
    main()