from typing import Dict, Iterable

from django.db import models

from slothql.selections import selections_to_dict, Selections


def get_forward_fields(model: models.Model) -> Dict[str, models.Field]:
    return {field.name: field for field in model._meta.get_fields()
            if isinstance(field, (models.ForeignKey, models.OneToOneField))}


def get_relation_fields(mode: models.Model) -> Dict[str, models.Field]:
    return {}


def get_selects(model: models.Model, root_selections: Selections) -> Iterable[str]:
    forward_relations = get_forward_fields(model)
    for name, selections in root_selections.items():
        if selections and name in forward_relations:
            model = forward_relations[name].target_field.model
            yield from ([f'{name}__{s}' for s in get_selects(model, selections)] or (name,))


def get_prefetches(model: models.Model, root_selections: Selections) -> Iterable[str]:
    relations = get_relation_fields(model)
    for name, selections in root_selections.items():
        if selections and name in relations:
            model = relations[name].target_field.model
            yield from ([f'{name}__{s}' for s in get_prefetches(model, selections)] or (name,))


def remove_selections(selections: Selections, selects: tuple):
    return selections


def get_optimized_queryset(manager: models.Manager, selections: Selections):
    queryset: models.QuerySet = manager.get_queryset()
    selects = tuple(get_selects(manager.model, selections))
    if selects:
        queryset = queryset.select_related(*selects)
        selections = remove_selections(selections, selects)
    prefetches = tuple(get_prefetches(manager.model, selections))
    if prefetches:
        queryset = queryset.prefetch_related(*prefetches)
    return queryset
