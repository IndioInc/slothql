from typing import List, Union, Dict, Optional

import graphql
from graphql.language import ast


Selections = Dict[str, Optional[dict]]


def get_selection_set(info: graphql.ResolveInfo) -> ast.SelectionSet:
    return info.operation.selection_set


def selections_to_dict(selections: List[ast.Field]) -> Selections:
    return {
        field.name: selections_to_dict(field.selection_set.selections) if field.selection_set else None
        for field in selections
    }


def get_selector(info: graphql.ResolveInfo):
    return selections_to_dict(get_selection_set(info).selections)
