import pytest

from slothql import ast

from .. import query_parser


@pytest.mark.parametrize(
    "value, cursor, expected",
    (
        ("", 0, ("", 0, query_parser.TokenType.EOF)),
        (" \n\t\r", 0, ("", 4, query_parser.TokenType.EOF)),
        ("{", 0, ("{", 1, query_parser.TokenType.OPEN_BODY)),
        ("}", 0, ("}", 1, query_parser.TokenType.CLOSE_BODY)),
        ("(", 0, ("(", 1, query_parser.TokenType.OPEN_ARGS)),
        (")", 0, (")", 1, query_parser.TokenType.CLOSE_ARGS)),
        ("null", 0, ("null", 4, query_parser.TokenType.NULL)),
        (":", 0, (":", 1, query_parser.TokenType.COLON)),
        ("foo", 0, ("foo", 3, query_parser.TokenType.NAME)),
        ("_foo", 0, ("_foo", 4, query_parser.TokenType.NAME)),
        ("f_oo", 0, ("f_oo", 4, query_parser.TokenType.NAME)),
        ("foo", 1, ("oo", 3, query_parser.TokenType.NAME)),
        ("123", 0, ("123", 3, query_parser.TokenType.INT)),
        ('"123"', 0, ('"123"', 5, query_parser.TokenType.STRING)),
        ('"123""foo"', 0, ('"123"', 5, query_parser.TokenType.STRING)),
        ("123.0", 0, ("123.0", 5, query_parser.TokenType.FLOAT)),
        ("foo{bar", 0, ("foo", 3, query_parser.TokenType.NAME)),
        ("foo{bar", 3, ("{", 4, query_parser.TokenType.OPEN_BODY)),
        ("foo{bar", 4, ("bar", 7, query_parser.TokenType.NAME)),
        ("#foo{\nbar\n", 0, ("bar", 9, query_parser.TokenType.NAME)),
        ("#\nfoo\nbar", 0, ("foo", 5, query_parser.TokenType.NAME)),
    ),
)
def test_parse_next(value: str, cursor: int, expected):
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
        (
            "{foo(a: 1)}",
            ast.AstQuery(
                operations=[
                    ast.AstOperation(
                        selections=[
                            ast.AstSelection(
                                name="foo",
                                arguments=[ast.AstArgument(name="a", value=1)],
                            )
                        ]
                    )
                ]
            ),
        ),
    ),
)
def test_parse_query__valid(query, expected):
    assert expected == query_parser.QueryParser(query).parse()


@pytest.mark.parametrize(
    "query, message",
    (
        ("", "Syntax Error GraphQL (1:1) Unexpected EOF"),
        ("}", "Syntax Error GraphQL (1:1) Unexpected }"),
        ("foo", 'Syntax Error GraphQL (1:1) Unexpected Name "foo"'),
        ("{", "Syntax Error GraphQL (1:2) Expected Name, found EOF"),
        ("{ą}", 'Syntax Error GraphQL (1:2) Unexpected character "ą"'),
        ("{}", "Syntax Error GraphQL (1:2) Expected Name, found }"),
        ("{{}", "Syntax Error GraphQL (1:2) Expected Name, found {"),
        ("{1}", 'Syntax Error GraphQL (1:2) Expected Name, found Int "1"'),
        ("{1.0}", 'Syntax Error GraphQL (1:2) Expected Name, found Float "1.0"'),
        ('{"foo"}', 'Syntax Error GraphQL (1:2) Expected Name, found String "foo"'),
        ("{'foo'}", 'Syntax Error GraphQL (1:2) Unexpected character "\'"'),
        ("{foo()}}", "Syntax Error GraphQL (1:6) Expected Name, found )"),
        ("{foo(bar)}}", "Syntax Error GraphQL (1:9) Expected :, found )"),
        ("{foo(bar:)}}", "Syntax Error GraphQL (1:10) Unexpected )"),
    ),
)
def test_parse_query__invalid(query, message):
    with pytest.raises(query_parser.QueryParseError) as exc_info:
        query_parser.QueryParser(query).parse()
    assert message == str(exc_info.value)
