import pytest

from slothql import ast
from .. import query_parser


@pytest.mark.parametrize(
    "query, stripped",
    (
        ("\n{\nversion#lol\n}\n", "{version}"),
        ("\t{\tversion\t}\t", " { version } "),
        ("# {version}", ""),
        ("{# {lol}\nversion}", "{version}"),
    ),
)
def test_strip_comments(query: str, stripped: str):
    assert stripped == query_parser.strip_comments(query)


@pytest.mark.parametrize(
    "value, cursor, expected",
    (
        ("", 0, query_parser.UnexpectedEOF()),
        ("text", 0, ("text", 4, query_parser.WORD_PATTERN)),
        ("text", 1, ("ext", 4, query_parser.WORD_PATTERN)),
        (" \n\t text", 0, ("text", 8, query_parser.WORD_PATTERN)),
        ("text{abc", 0, ("text", 4, query_parser.WORD_PATTERN)),
        ("text(abc", 0, ("text", 4, query_parser.WORD_PATTERN)),
        ("text{abc", 4, ("{", 5, query_parser.BRACKET_PATTERN)),
        ("text{abc", 5, ("abc", 8, query_parser.WORD_PATTERN)),
    ),
)
def test_parse_next(value: str, cursor: int, expected):
    if isinstance(expected, Exception):
        with pytest.raises(type(expected)) as exc_info:
            query_parser.parse_next(value, cursor)

        assert isinstance(exc_info.value, type(expected)) and str(expected) == str(
            exc_info.value
        )
    else:
        assert expected == query_parser.parse_next(value, cursor)


@pytest.mark.skip
@pytest.mark.parametrize(
    "query, expected",
    (
        ("{version}", ast.AstQuery(selections=[ast.AstSelection(name="version")])),
        (
            "query {version}",
            ast.AstQuery(selections=[ast.AstSelection(name="version")]),
        ),
        (
            "query query {version}",
            ast.AstQuery(selections=[ast.AstSelection(name="version")]),
        ),
    ),
)
def test_parse_query(query, expected):
    if isinstance(expected, Exception):
        with pytest.raises(type(Exception)) as exc_info:
            query_parser.QueryParser(query).parse()
        assert expected == exc_info.value
    else:
        assert expected == query_parser.QueryParser(query).parse()
