import time
import logging
import argparse
from pathlib import Path
from .api import fetch_data
from .export import save_csv
from .transform import transform_items
from .database import db_init, save_to_db

logger = logging.getLogger(__name__)


def setup_logging():
    Path("logs").mkdir(exist_ok=True)

    logging.basicConfig(
        filename="logs/books_parser.log",
        level=logging.INFO,
        encoding="utf-8",
        format="[%(asctime)s] - %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--output", default="data/books.csv")
    parser.add_argument("--db", default="data/books.db")
    parser.add_argument("--query", default="python")
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--limit", type=int, default=50)

    return parser.parse_args()


def parse_all_pages(pages, query, limit):
    all_books = []

    for page in range(1, pages + 1):
        raw_items = fetch_data(query, page, limit)
        if raw_items is None:
            logger.warning(f"API request failed on page %s. STOP", page)
            break

        clean_items = transform_items(raw_items)
        if not clean_items:
            logger.warning("Cleanup was unsuccessful. STOP")
            break

        all_books.extend(clean_items)

        logger.info(f"Parsed page: %s, books found: %s", page, len(clean_items))

        time.sleep(0.5)

    return all_books


def main():
    setup_logging()

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