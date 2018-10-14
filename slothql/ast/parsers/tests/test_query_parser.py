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
