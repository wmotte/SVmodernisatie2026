"""Bekende correcties op SV1657-bronverwijzingen voor compare-scaffolding."""

SOURCE_TEXT_CORRECTIONS = {
    ("COL", 1, 13): {
        "$Matth. 3.17. ende 17.15. 2.Petr. 1.17.$": "$Matth. 3.17. ende 17.5. 2.Petr. 1.17.$",
        "$Mt. 3:17; 17:15; 2Pt. 1:17$": "$Mt. 3:17; 17:5; 2Pt. 1:17$",
    },
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
