import re
import string
import typing as t

from slothql import ast


class QueryParseError(Exception):
    pass


class UnexpectedEOF(QueryParseError):
    pass


class ClosingBracketNotFound(QueryParseError):
    pass


def strip_comments(query: str) -> str:
    def strip():
        for line in query.replace("\t", " ").split("\n"):
            if "#" in line:
                yield from line[: line.index("#")]
            else:
                yield from line

    return "".join(strip())


WORD_PATTERN = re.compile(r"[a-zA-Z_]\w*")
BRACKET_PATTERN = re.compile(r"[{}()]")

TOKENS: t.List[t.Pattern] = [WORD_PATTERN, BRACKET_PATTERN]


def parse_next(value: str, cursor: int) -> t.Tuple[str, int, t.Pattern]:
    for i, char in enumerate(value[cursor:]):
        if char in string.whitespace:
            continue
        for token_pattern in TOKENS:
            if re.match(token_pattern, char):
                token = next(re.finditer(token_pattern, value[cursor + i:])).group()
                return token, cursor + i + len(token), token_pattern
    raise UnexpectedEOF()


class QueryParser:
    def __init__(self, query: str) -> None:
        assert isinstance(
            query, str
        ), f"expected query to be of type str, not {repr(query)}"
        self.query = strip_comments(query)

    def parse(self) -> ast.AstQuery:
        pass

    def _get_operations(self) -> t.Iterable[str]:
        pass
