
"""Shared setup for Find-A-Time browser acceptance tests."""

import urllib.error
import urllib.request

import pytest

BASE_URL = "http://127.0.0.1:5000"


def pytest_sessionstart(session):
    """Check that the application is running before tests begin."""
    health_url = f"{BASE_URL}/health"

    try:
        with urllib.request.urlopen(health_url, timeout=1.0) as response:
            if response.status != 200:
                pytest.exit(
                    f"{health_url} returned {response.status}. "
                    "Check that the application and database are running.",
                    returncode=1,
                )
    except (urllib.error.URLError, OSError) as exc:
        pytest.exit(
            f"Cannot reach the application at {BASE_URL}. "
            "Start DynamoDB Local and run the Flask application first.\n"
            f"Details: {exc}",
            returncode=1,
        )


@pytest.fixture(scope="session")
def base_url():
    """Base URL used by Playwright for relative navigation."""
    return BASE_URL
