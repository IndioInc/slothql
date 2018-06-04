import typing as t

from django.db import models

from slothql.selections import Selections, Selection
from .utils.model import get_selectable_relations, get_relations, Relation


def get_selects(model: t.Type[models.Model], root_selections: Selections) -> t.Iterable[str]:
    forward_relations = get_selectable_relations(model)
    for name, selections in root_selections.items():
        if selections and name in forward_relations:
            yield from ([f'{name}__{s}' for s in get_selects(forward_relations[name], selections)] or (name,))


def get_prefetches(model: t.Type[models.Model], root_selections: Selections) -> t.Iterable[str]:
    relations = get_relations(model)
    for name, selections in root_selections.items():
        if selections and name in relations:
            yield from ([f'{name}__{s}' for s in get_prefetches(relations[name], selections)] or (name,))


def remove_selections(selections: Selections, selects: tuple):
    return selections


def get_optimized_queryset(manager: models.Manager, selections: Selections):
    queryset: models.QuerySet = manager.get_queryset()
    # selects = tuple(get_selects(manager.model, selections))
    # if selects:
    #     queryset = queryset.select_related(*selects)
    #     selections = remove_selections(selections, selects)
    prefetches = tuple(get_prefetches(manager.model, selections))
    if prefetches:
        queryset = queryset.prefetch_related(*prefetches)
    return queryset


def apply_selections(queryset: models.QuerySet, selections: t.Iterable[Selection]) -> models.QuerySet:
    return select_related(queryset, selections)


def select_related(queryset: models.QuerySet, selections: t.Iterable[Selection]) -> models.QuerySet:
    fields = [s.field_name for s in selections]
    return queryset.select_related(*(
        relation.name for relation in Relation.get_selectable(model=queryset.model)
        if relation.name in fields
    ))
