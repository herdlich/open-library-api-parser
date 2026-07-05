import logging
from urllib.parse import urljoin

BOOK_URL = "https://openlibrary.org"

logger = logging.getLogger(__name__)


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
                logger.warning("Work key not found. SKIP book")
                continue

            link = urljoin(BOOK_URL, work_key)

            book_id = work_key.split("/")[-1]
            if not book_id:
                logger.warning("Book ID not found. SKIP book")
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
