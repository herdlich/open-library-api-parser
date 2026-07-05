import requests
import logging

API_URL = "https://openlibrary.org/search.json"

logger = logging.getLogger(__name__)


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
        logger.error("Request error: %s", error)
        return None
