from django.db import models

from slothql.selections import Selection

from .utils.model import Relation


def select_related(queryset: models.QuerySet, selection: Selection) -> models.QuerySet:
    fields = [s.field_name for s in selection.selections]
    return queryset.select_related(*(
        relation.name for relation in Relation.get_selectable(model=queryset.model) if relation.name in fields
    ))


def prefetch_related(queryset: models.QuerySet, selection: Selection) -> models.QuerySet:
    fields = [s.field_name for s in selection.selections]
    return queryset.prefetch_related(*(
        models.Prefetch(
            lookup=relation.name,
            queryset=filter_queryset(relation.model._default_manager.get_queryset(),
                                     next(s for s in selection.selections if s.field_name == relation.name)),
        )
        for relation in Relation.get_prefetchable(model=queryset.model) if relation.name in fields
    ))


def filter_queryset(queryset: models.QuerySet, selection: Selection):
    if not selection.filters:
        return queryset
    kwargs = {
        expression.path.replace('.', '__'): expression.value
        for expression in selection.filters
    }
    return queryset.filter(**kwargs)
