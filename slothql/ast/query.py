from __future__ import annotations

import dataclasses
import typing as t


@dataclasses.dataclass()
class AstParameter:
    name: str
    typename: str


@dataclasses.dataclass()
class AstVariable:
    name: str


AstValue = t.Union[str, float, int, bool, None, list, dict]


@dataclasses.dataclass()
class AstArgument:
    name: str
    value: t.Union[AstValue, AstVariable]


@dataclasses.dataclass()
class AstSelection:
    name: str
    arguments: t.Optional[t.List[AstArgument]] = None
    selections: t.Optional[t.List["AstSelection"]] = None


@dataclasses.dataclass()
class AstOperation:
    selections: t.List[AstSelection]
    name: t.Optional[str] = None
    variables: t.List[AstParameter] = dataclasses.field(default_factory=list)


@dataclasses.dataclass()
class AstQuery:
    operations: t.List[AstOperation]
