import pytest

from slothql import ast
from slothql.utils.test import assert_exception

from .. import query_parser


@pytest.mark.parametrize(
    "value, cursor, expected",
    (
        ("", 0, ("", 0, query_parser.TokenType.EOF)),
        ("{", 0, ("{", 1, query_parser.TokenType.OPEN_BODY)),
        ("}", 0, ("}", 1, query_parser.TokenType.CLOSE_BODY)),
        ("foo", 0, ("foo", 3, query_parser.TokenType.NAME)),
        ("foo", 1, ("oo", 3, query_parser.TokenType.NAME)),
        (" \n\t foo", 0, ("foo", 7, query_parser.TokenType.NAME)),
        ("foo{bar", 0, ("foo", 3, query_parser.TokenType.NAME)),
        ("foo{bar", 3, ("{", 4, query_parser.TokenType.OPEN_BODY)),
        ("foo{bar", 4, ("bar", 7, query_parser.TokenType.NAME)),
        (" \t\nfoo", 0, ("foo", 6, query_parser.TokenType.NAME)),
        ("#foo{\nbar\n", 0, ("bar", 9, query_parser.TokenType.NAME)),
        ("#\nfoo\nbar", 0, ("foo", 5, query_parser.TokenType.NAME)),
    ),
)
def test_parse_next(value: str, cursor: int, expected):
    with assert_exception(expected if isinstance(expected, Exception) else None):
        assert expected == query_parser.parse_next(value, cursor)


@pytest.mark.parametrize(
    "query, expected",
    (
        (
            "{foo}",
            ast.AstQuery(
                operations=[ast.AstOperation(selections=[ast.AstSelection(name="foo")])]
            ),
        ),
        (
            "query {foo}",
            ast.AstQuery(
                operations=[ast.AstOperation(selections=[ast.AstSelection(name="foo")])]
            ),
        ),
        (
            "query foo {bar}",
            ast.AstQuery(
                operations=[
                    ast.AstOperation(
                        name="foo", selections=[ast.AstSelection(name="bar")]
                    )
                ]
            ),
        ),
        (
            "query q {foo \nsub {bar baz}}",
            ast.AstQuery(
                operations=[
                    ast.AstOperation(
                        name="q",
                        selections=[
                            ast.AstSelection(name="foo"),
                            ast.AstSelection(
                                name="sub",
                                selections=[
                                    ast.AstSelection(name="bar"),
                                    ast.AstSelection(name="baz"),
                                ],
                            ),
                        ],
                    )
                ]
            ),
        ),
    ),
)
def test_parse_query(query, expected):
    with assert_exception(expected if isinstance(expected, Exception) else None):
        assert expected == query_parser.QueryParser(query).parse()
