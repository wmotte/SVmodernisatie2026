"""Bekende correcties op SV1657-bronverwijzingen voor compare-scaffolding."""

SOURCE_TEXT_CORRECTIONS = {
    ("LUK", 1, 53): {
        "$Psalm 43.11$": "$Psalm 34.11$",
        "$Ps. 43:11$": "$Ps. 34:11$",
    },
}


def apply_source_corrections(book: str, chapter: int, verse: int, text: str) -> str:
    corrections = SOURCE_TEXT_CORRECTIONS.get((book, int(chapter), int(verse)), {})
    for old, new in corrections.items():
        text = text.replace(old, new)
    return text
