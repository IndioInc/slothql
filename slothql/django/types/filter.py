import typing as t

from django.db import models

from slothql.types.fields.filter import Filter, FilterMeta, FilterOptions


class DjangoFilterOptions(FilterOptions):
    __slots__ = ('model',)
    model: t.Type[models.Model]


class DjangoFilterMeta(FilterMeta):
    _meta: DjangoFilterOptions

    def __new__(mcs, name: str, bases: t.Tuple[type], attrs: dict,
                options_class: t.Type[DjangoFilterOptions] = DjangoFilterOptions, **kwargs):
        return super().__new__(mcs, name, bases, attrs, options_class, **kwargs)


class DjangoFilter(Filter, metaclass=DjangoFilterMeta):
    _meta: DjangoFilterOptions

    def apply(self, queryset: models.QuerySet) -> models.QuerySet:
        assert isinstance(queryset, models.QuerySet), f'Expected QuerySet, but received {queryset}'
        for field, value in self.filter_fields.items():
            if value is None:
                queryset = queryset.filter(**{f'{field}__isnull': True})
            else:
                queryset = queryset.filter(**{field: value})
        return queryset
