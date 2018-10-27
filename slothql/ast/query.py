from __future__ import annotations

import dataclasses
import typing as t

AstValue = t.Union[str, float, int, bool, None, list, dict]


@dataclasses.dataclass()
class AstArgument:
    name: str
    value: AstValue


@dataclasses.dataclass()
class AstSelection:
    name: str
    arguments: t.Optional[t.List[AstArgument]] = None
    selections: t.Optional[t.List["AstSelection"]] = None


@dataclasses.dataclass()
class AstOperation:
    selections: t.List[AstSelection]
    name: t.Optional[str] = None


@dataclasses.dataclass()
class AstQuery:
    operations: t.List[AstOperation]
