import csv
from pathlib import Path


def save_csv(csv_file, csv_data):
    Path(csv_file).parent.mkdir(parents=True, exist_ok=True)

    with open(csv_file, "w", encoding="utf-8", newline="") as file:
        fieldnames = ["book_id", "title", "author_name", "first_publish_year", "language", "edition_count", "cover_i",
                      "cover_link", "ia", "link"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(csv_data)
