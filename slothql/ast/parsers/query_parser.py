import typing as t

from slothql import ast


class QueryParseError(Exception):
    pass


def strip_comments(query: str) -> str:
    def strip():
        for line in query.replace("\t", " ").split("\n"):
            if "#" in line:
                yield from line[: line.index("#")]
            else:
                yield from line

    return "".join(strip())


def get_matching_bracket_index(open_bracket: str, close_bracket: str) -> int:
    pass


class QueryParser:
    def __init__(self, query: str):
        assert isinstance(
            query, str
        ), f"expected query to be of type str, not {repr(query)}"
        self.query = strip_comments(query)

    def parse(self) -> ast.AstQuery:
        pass

    def _get_operations(self) -> t.Iterable[str]:
        pass
