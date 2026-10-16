"""Tests the creation of an event."""

"""Commented out due to being incomplte."""


"""
def test_create_event_navigates_to_availability_page(page, base_url):
    page.goto(f"{base_url}/events/new")

    page.locator("#event-name").fill("CS Study Group")
    page.locator("#creator-name").fill("Joshua")

    # The form starts with two time inputs.
    page.locator(".time-input").nth(0).fill("2026-11-02T10:00")
    page.locator(".time-input").nth(1).fill("2026-11-03T14:00")

    page.get_by_role("button", name="Create event").click()

    page.wait_for_url("**/events/*/availability")

    # Confirm the URL contains a numeric event ID.
    assert page.url.endswith("/availability")
    event_id = page.url.split("/events/")[1].split("/")[0]
    assert event_id.isdigit()
"""


