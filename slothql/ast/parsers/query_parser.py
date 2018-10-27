import dataclasses
import re
import typing as t

from slothql import ast


def get_position_from_cursor(query: str, cursor: int) -> t.Tuple[int, int]:
    line = query[:cursor].count("\n")
    line_start = 0 if "\n" not in query else query.index("\n", cursor, 0)
    column = len(query[line_start:cursor])
    return line, column


def escape_whitespace(query: str) -> str:
    return query.replace("\n", "\\n").replace("\t", "\\t")


class QueryParseError(Exception):
    def __init__(self, message: str, line: int = None, column: int = None):
        self.message = escape_whitespace(message)
        self.line = line
        self.column = column

    @property
    def position(self) -> str:
        if self.line and self.column:
            return f"({self.line}:{self.column})"
        return ""

    def __str__(self):
        return f"GraphQL parse error{self.position}: {self.message}"

    def __repr__(self):
        return f'{type(self).__name__}(message="{self.message}")'


class Token(t.NamedTuple):
    verbose: str
    pattern: t.Pattern
    skip: bool = False


class TokenType:
    NAME = Token(verbose="name", pattern=re.compile(r"^[a-zA-Z_]\w*"))
    OPEN_BODY = Token(verbose="{", pattern=re.compile(r"^{"))
    CLOSE_BODY = Token(verbose="}", pattern=re.compile(r"^}"))
    EOF = Token(verbose="EOF", pattern=re.compile(r"^$"))
    WHITESPACE = Token(verbose="whitespace", pattern=re.compile(r"^\s"), skip=True)
    COMMENT = Token(verbose="comment", pattern=re.compile(r"^#.*\n"), skip=True)

    ALL = {NAME, OPEN_BODY, CLOSE_BODY, EOF, WHITESPACE, COMMENT}


def parse_next(value: str, cursor: int) -> t.Tuple[str, int, Token]:
    new_cursor = cursor
    while True:
        for token in TokenType.ALL:
            if re.match(token.pattern, value[new_cursor:]):
                matched_token = next(
                    re.finditer(token.pattern, value[new_cursor:])
                ).group()
                new_cursor += len(matched_token)
                if token.skip:
                    return parse_next(value, new_cursor)
                return matched_token, new_cursor, token
        raise QueryParseError(f"Invalid character encountered: `{value[new_cursor]}`")


class QueryParser:
    def __init__(self, query: str) -> None:
        assert isinstance(
            query, str
        ), f"expected query to be of type str, not {repr(query)}"
        self.query = query
        self.cursor = 0

    @property
    def position(self) -> t.Tuple[int, int]:
        return get_position_from_cursor(self.query, self.cursor)

    def next(self, *, expected: t.Set[Token]) -> t.Tuple[str, Token]:
        parsed, self.cursor, token = parse_next(self.query, self.cursor)
        if token not in expected:
            raise QueryParseError(
                f"Unexpected {token.verbose} {parsed}. Expected ("
                + ", ".join(f"`{i.verbose}`" for i in expected)
                + ")"
            )
        return parsed, token

    def parse(self) -> ast.AstQuery:
        operation = self._parse_operation()
        return ast.AstQuery(operations=[operation])

    def _parse_selections(self) -> t.Iterator[ast.AstSelection]:
        name, token = self.next(expected={TokenType.NAME})
        selection = ast.AstSelection(name=name)
        while True:
            name, token = self.next(
                expected={TokenType.NAME, TokenType.OPEN_BODY, TokenType.CLOSE_BODY}
            )
            if token is TokenType.NAME:
                yield selection
                selection = ast.AstSelection(name=name)
            elif token is TokenType.OPEN_BODY:
                selection = dataclasses.replace(
                    selection, selections=list(self._parse_selections())
                )
            elif token is TokenType.CLOSE_BODY:
                yield selection
                break

    def _parse_operation(self) -> ast.AstOperation:
        operation_name = None

        parsed, token = self.next(expected={TokenType.NAME, TokenType.OPEN_BODY})
        if token is TokenType.NAME:
            if parsed not in ("query", "mutation"):
                raise QueryParseError(f'Invalid name "{parsed}"', *self.position)

            parsed, token = self.next(expected={TokenType.NAME, TokenType.OPEN_BODY})
            if token is TokenType.NAME:
                operation_name = parsed
                parsed, token = self.next(
                    expected={TokenType.NAME, TokenType.OPEN_BODY}
                )

        assert token is TokenType.OPEN_BODY

        return ast.AstOperation(
            name=operation_name, selections=list(self._parse_selections())
        )
