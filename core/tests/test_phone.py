import pytest

from core.phone import normalize_phone


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("671234567", "+237671234567"),
        ("671 23 45 67", "+237671234567"),
        ("671-23-45-67", "+237671234567"),
        ("+237 671 23 45 67", "+237671234567"),
        ("237 671 23 45 67", "+237671234567"),
        ("00237 671 23 45 67", "+237671234567"),
    ],
)
def test_normalize_phone_equivalent_formats(raw, expected):
    assert normalize_phone(raw) == expected


def test_normalize_phone_is_idempotent():
    once = normalize_phone("671 23 45 67")
    twice = normalize_phone(once)
    assert once == twice
