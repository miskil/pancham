DEVANAGARI_TO_ASCII = str.maketrans({
    "०": "0",
    "१": "1",
    "२": "2",
    "३": "3",
    "४": "4",
    "५": "5",
    "६": "6",
    "७": "7",
    "८": "8",
    "९": "9",
})


def normalize_localized_digits(value: str) -> str:
    return value.translate(DEVANAGARI_TO_ASCII)


def parse_locale_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        raise ValueError("Invalid number")

    normalized = normalize_localized_digits(value).replace(",", "").strip()
    if normalized == "":
        return None
    try:
        return float(normalized)
    except ValueError as exc:
        raise ValueError("Invalid number") from exc
