from ast import literal_eval
import dataclasses
import itertools
import re
import typing as t

from slothql import ast


def get_position_from_cursor(value: str, cursor: int) -> t.Tuple[int, int]:
    assert cursor <= len(
        value
    ), f"Cursor out of range, received {cursor} for len(value)={len(value)}"
    line = value[:cursor].count("\n")
    column = len(
        "".join(itertools.takewhile(lambda i: i != "\n", reversed(value[:cursor])))
    )
    return line + 1, column + 1


@dataclasses.dataclass()
class QueryParseError(Exception):
    message: str
    query: str
    cursor: int
    line: int = dataclasses.field(init=False)
    column: int = dataclasses.field(init=False)

    def __post_init__(self):
        self.line, self.column = get_position_from_cursor(self.query, self.cursor)

    def __str__(self):
        return f"Syntax Error GraphQL ({self.line}:{self.column}) {self.message}"

    def __repr__(self):
        return f'{type(self).__name__}(message="{self.message}")'


class Token(t.NamedTuple):
    name: str
    pattern: t.Pattern
    verbose: t.Optional[t.Callable[[str], str]] = None
    serialize: t.Optional[t.Callable[[str], t.Any]] = None
    is_syntax_error: bool = False
    skip: bool = False


class TokenType:
    NULL = Token(name="null", pattern=re.compile(r"^null"), serialize=lambda _: None)
    NAME = Token(
        name="Name", verbose=lambda v: f'"{v}"', pattern=re.compile(r"^[a-zA-Z_]\w*")
    )
    FLOAT = Token(
        name="Float",
        verbose=lambda v: f'"{v}"',
        pattern=re.compile(r"^\d+\.\d+"),
        serialize=float,
    )
    INT = Token(
        name="Int",
        verbose=lambda v: f'"{v}"',
        pattern=re.compile(r"^\d+"),
        serialize=int,
    )
    STRING = Token(
        name="String",
        verbose=lambda v: f"{v}",
        pattern=re.compile(r"^\"(\\.|[^\"\n\\])*\""),
        serialize=literal_eval,
    )
    VARIABLE = Token(
        name="Variable",
        verbose=lambda v: f'"{v[1:]}"',
        pattern=re.compile(r"^\$([a-zA-Z_])\w*"),
        serialize=lambda v: ast.AstVariable(name=v[1:]),
    )
    EOF = Token(name="EOF", pattern=re.compile(r"^$"))
    QUERY = Token(name="query", pattern=re.compile(r"^query"))
    OPEN_BODY = Token(name="{", pattern=re.compile(r"^{"))
    CLOSE_BODY = Token(name="}", pattern=re.compile(r"^}"))
    OPEN_ARGS = Token(name="(", pattern=re.compile(r"^\("))
    CLOSE_ARGS = Token(name=")", pattern=re.compile(r"^\)"))
    COLON = Token(name=":", pattern=re.compile(r"^:"))
    COMMA = Token(name=",", pattern=re.compile(r"^,"))
    DOLLAR = Token(name="$", pattern=re.compile(r"^\$"))
    DIRECTIVE = Token(name="@", pattern=re.compile(r"^@"))
    WHITESPACE = Token(name="whitespace", pattern=re.compile(r"^\s"), skip=True)
    COMMENT = Token(name="comment", pattern=re.compile(r"^#[^\n]*\n"), skip=True)
    UNTERMINATED_STRING = Token(
        name="Unterminated string",
        pattern=re.compile(r"^\"(\\.|[^\n\"\\])*"),
        is_syntax_error=True,
    )

    @classmethod
    def all(cls) -> t.Iterable[Token]:
        yield from (i for i in vars(cls).values() if isinstance(i, Token))


def parse_next(
    value: str, cursor: int, tokens: t.Iterable[Token] = None
) -> t.Tuple[str, int, Token]:
    for token in itertools.chain(tokens or [], TokenType.all()):
        if re.match(token.pattern, value[cursor:]):
            raw = next(re.finditer(token.pattern, value[cursor:])).group()
            cursor += len(raw)
            if token.skip:
                return parse_next(value, cursor, tokens)
            if token.is_syntax_error:
                raise QueryParseError(token.name, value, cursor)
            return raw, cursor, token
    raise QueryParseError(f'Unexpected character "{value[cursor]}"', value, cursor)


class QueryParser:
    def __init__(self, query: str) -> None:
        assert isinstance(
            query, str
        ), f"expected query to be of type str, not {repr(query)}"
        self.query = query
        self.cursor = 0
        self.parsed: str = ""
        self.token: t.Optional[Token] = None

    def next(self, *, expected: t.List[Token]) -> None:
        self.parsed, new_cursor, self.token = parse_next(
            self.query, self.cursor, expected
        )
        if self.token not in expected:
            if len(expected) == 1:
                message = f"Expected {expected[0].name}, found {self.token.name}"
            else:
                message = f"Unexpected {self.token.name}"
            verbose = (
                f" {self.token.verbose(self.parsed)}" if self.token.verbose else ""
            )
            raise QueryParseError(message + verbose, self.query, self.cursor)
        self.cursor = new_cursor

    def parse(self) -> ast.AstQuery:
        operation = self._parse_operation()
        return ast.AstQuery(operations=[operation])

    def _parse_operation(self) -> ast.AstOperation:
        operation_name = None
        variables = []

        self.next(expected=[TokenType.QUERY, TokenType.OPEN_BODY])
        if self.token is TokenType.QUERY:
            self.next(expected=[TokenType.NAME, TokenType.OPEN_BODY])
            if self.token is TokenType.NAME:
                operation_name = self.parsed
                self.next(expected=[TokenType.OPEN_ARGS, TokenType.OPEN_BODY])
                if self.token is TokenType.OPEN_ARGS:
                    variables = list(self._parse_operation_args())
                    self.next(expected=[TokenType.OPEN_BODY])

        assert self.token is TokenType.OPEN_BODY

        return ast.AstOperation(
            name=operation_name,
            selections=list(self._parse_selections()),
            variables=variables,
        )

    def _parse_operation_args(self) -> t.Iterator[ast.AstParameter]:
        while True:
            self.next(expected=[TokenType.DOLLAR])
            self.next(expected=[TokenType.NAME])
            name = self.parsed
            self.next(expected=[TokenType.COLON])
            self.next(expected=[TokenType.NAME])
            yield ast.AstParameter(name=name, typename=self.parsed)
            self.next(expected=[TokenType.COMMA, TokenType.CLOSE_ARGS])
            if self.token is TokenType.CLOSE_ARGS:
                break

    def _parse_selections(self) -> t.Iterator[ast.AstSelection]:
        selection = None
        self.next(expected=[TokenType.NAME])
        while True:
            if self.token is TokenType.DIRECTIVE:
                selection = dataclasses.replace(
                    selection, directives=list(self._parse_directives())
                )
            if self.token is TokenType.NAME:
                if selection:
                    yield selection
                selection = ast.AstSelection(name=self.parsed)
            elif self.token is TokenType.OPEN_ARGS:
                selection = dataclasses.replace(
                    selection, arguments=list(self._parse_arguments())
                )
            elif self.token is TokenType.OPEN_BODY:
                selection = dataclasses.replace(
                    selection, selections=list(self._parse_selections())
                )
            elif self.token is TokenType.CLOSE_BODY:
                yield selection
                break
            else:
                raise AssertionError(f"Unhandled token: {repr(self.token)}")

            self.next(
                expected=[
                    TokenType.NAME,
                    TokenType.DIRECTIVE,
                    TokenType.OPEN_BODY,
                    TokenType.CLOSE_BODY,
                    TokenType.OPEN_ARGS,
                ]
            )

    def _parse_arguments(self) -> t.Iterator[ast.AstArgument]:
        while True:
            self.next(expected=[TokenType.NAME])
            name = self.parsed
            self.next(expected=[TokenType.COLON])
            self.next(
                expected=[
                    TokenType.FLOAT,
                    TokenType.INT,
                    TokenType.STRING,
                    TokenType.VARIABLE,
                    TokenType.NULL,
                ]
            )
            yield ast.AstArgument(name=name, value=self.token.serialize(self.parsed))
            self.next(expected=[TokenType.COMMA, TokenType.CLOSE_ARGS])
            if self.token is TokenType.CLOSE_ARGS:
                break

    def _parse_directives(self) -> t.Iterable[ast.AstDirective]:
        self.next(expected=[TokenType.NAME])
        directive = ast.AstDirective(name=self.parsed)
        while True:
            self.next(
                expected=[
                    TokenType.DIRECTIVE,
                    TokenType.OPEN_ARGS,
                    TokenType.NAME,
                    TokenType.OPEN_BODY,
                    TokenType.CLOSE_BODY,
                ]
            )
            if self.token is TokenType.OPEN_ARGS:
                directive = dataclasses.replace(
                    directive, arguments=list(self._parse_arguments())
                )
                self.next(
                    expected=[
                        TokenType.DIRECTIVE,
                        TokenType.NAME,
                        TokenType.OPEN_BODY,
                        TokenType.CLOSE_BODY,
                    ]
                )
            if self.token in (
                TokenType.OPEN_BODY,
                TokenType.CLOSE_BODY,
                TokenType.NAME,
            ):
                yield directive
                break
            if self.token is TokenType.DIRECTIVE:
                yield directive
                self.next(expected=[TokenType.NAME])
                directive = ast.AstDirective(name=self.parsed)
