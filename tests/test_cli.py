from open_library_parser.cli import parse_all_pages


def test_parse_all_pages_full(monkeypatch):
    def fake_fetch_data(query, page, limit):
        return {"page": page}

    def fake_transform_items(data):
        return [{"book_id": data["page"]}]

    monkeypatch.setattr(
        "open_library_parser.cli.fetch_data",
        fake_fetch_data
    )
    monkeypatch.setattr(
        "open_library_parser.cli.transform_items",
        fake_transform_items
    )
    monkeypatch.setattr(
        "open_library_parser.cli.time.sleep",
        lambda seconds: None
    )

    result = parse_all_pages(3, "query", 100)
    expected_books = [
        {"book_id": 1, },
        {"book_id": 2, },
        {"book_id": 3, }
    ]

    assert expected_books == result


def test_incomplete_pages_in_parse_all_pages(monkeypatch):
    all_pages = []

    def fake_fetch_data(query, page, limit):
        all_pages.append(page)

        if page == 1:
            return {"page": page}

        elif page == 2:
            return None

        return {"page": page}

    def fake_transform_items(data):
        return [{"book_id": data["page"]}]

    monkeypatch.setattr(
        "open_library_parser.cli.fetch_data",
        fake_fetch_data
    )
    monkeypatch.setattr(
        "open_library_parser.cli.transform_items",
        fake_transform_items
    )
    monkeypatch.setattr(
        "open_library_parser.cli.time.sleep",
        lambda seconds: None
    )

    result = parse_all_pages(3, "query", 100)
    expected_books = [
        {"book_id": 1},
    ]

    assert all_pages == [1, 2]
    assert expected_books == result


def test_break_in_clean_items(monkeypatch):
    transformed_pages = []

    def fake_fetch_data(query, page, limit):
        return {"page": page}

    def fake_transform_items(data):
        transformed_pages.append(data["page"])
        if data["page"] == 2:
            return []

        return [{"book_id": data["page"]}]

    monkeypatch.setattr(
        "open_library_parser.cli.fetch_data",
        fake_fetch_data
    )
    monkeypatch.setattr(
        "open_library_parser.cli.transform_items",
        fake_transform_items
    )
    monkeypatch.setattr(
        "open_library_parser.cli.time.sleep",
        lambda seconds: None
    )

    result = parse_all_pages(3, "query", 100)
    expected_books = [
        {"book_id": 1}
    ]

    assert transformed_pages == [1, 2]
    assert expected_books == result
