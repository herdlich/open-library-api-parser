import time
import requests
import logging

API_URL = "https://openlibrary.org/search.json"

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = (
    429,
    500,
    502,
    503,
    504,
)


def fetch_data(
        query: str,
        page: int,
        limit: int,
        max_attempts: int = 3
) -> dict | None:
    params = {
        "q": query,
        "page": page,
        "limit": limit
    }

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=10
            )

            if response.status_code in RETRYABLE_STATUS_CODES:
                raise requests.HTTPError(
                    f"Temporary HTTP error: {response.status_code}",
                    response=response
                )

            response.raise_for_status()
            return response.json()

        except requests.Timeout as error:
            logger.error(
                "Timeout. Attempt %s/%s: %s",
                attempt,
                max_attempts,
                error
            )

        except requests.ConnectionError as error:
            logger.error(
                "Connection error. Attempt %s/%s: %s",
                attempt,
                max_attempts,
                error
            )

        except requests.HTTPError as error:
            status_code = (
                error.response.status_code
                if error.response is not None
                else None
            )

            if status_code not in RETRYABLE_STATUS_CODES:
                logger.error(
                    "Non-retryable HTTP error: %s",
                    status_code
                )

                return None

            logger.warning(
                "Temporary HTTP error %s. Attempt %s/%s",
                status_code,
                attempt,
                max_attempts
            )

        except requests.RequestException as error:
            logger.error("Request error: %s", error)
            return None

        if attempt < max_attempts:
            delay = 2 ** (attempt - 1)
            time.sleep(delay)

    logger.error(
        "All items failed for page %s",
        page
    )

    return None
