import requests
from open_library_parser.api import fetch_data


def test_fetch_data_returns_json(monkeypatch):
    expected_data = {
        "docs": [
            {
                "key": "/works/OL123W",
                "title": "Python Basics",
            }
        ]
    }

    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return expected_data

    def fake_get(url, params, timeout):
        assert url == "https://openlibrary.org/search.json"
        assert params == {
            "q": "python",
            "page": 1,
            "limit": 50,
        }
        assert timeout == 10

        return FakeResponse()

    monkeypatch.setattr(
        "open_library_parser.api.requests.get",
        fake_get,
    )

    result = fetch_data(
        query="python",
        page=1,
        limit=50,
    )

    assert result == expected_data


def test_fetch_data_returns_none_on_request_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.RequestException("Connection failed")

    monkeypatch.setattr(
        "open_library_parser.api.requests.get",
        fake_get,
    )

    result = fetch_data(
        query="python",
        page=1,
        limit=50
    )

    assert result is None
