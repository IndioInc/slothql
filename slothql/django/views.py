import json
from collections import OrderedDict

from django.template import Template
from django.template.context import Context
from typing import Tuple, Optional, Union, Callable

from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.views import View
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, JsonResponse

from graphql.type.schema import GraphQLSchema

import slothql
from slothql.operation import OperationSyntaxError
from slothql.template import get_template_string

from .utils.request import get_operation_from_request


class GraphQLView(View):
    DEBUG = True
    allowed_methods = ('GET', 'POST')

    graphiql_version: str = '0.11.10'
    graphiql_template: str = 'graphiql.html'

    schema: Union[GraphQLSchema, Callable] = None

    @classmethod
    def as_view(cls, **initkwargs):
        schema = initkwargs.get('schema')
        assert schema is not None, f'Expected schema to be of type Schema, but got {schema}'
        return super().as_view(**initkwargs)

    def dispatch(self, request: WSGIRequest, *args, **kwargs) -> HttpResponse:
        if request.method not in self.allowed_methods:
            return HttpResponseNotAllowed(['GET', 'POST'], 'GraphQL supports only GET and POST requests.')

        try:
            query = self.get_operation()
        except OperationSyntaxError as e:
            return JsonResponse({'errors': [{'message': str(e)}]}, status=400)

        result, status_code = self.get_query_result(query)
        if self.show_graphiql:
            template = Template(get_template_string(self.graphiql_template))
            context = Context({**self.get_context_data(), **{'result': result if query else '', 'query': query}})
            return HttpResponse(template.render(context), status=status_code if query else 200)

        return HttpResponse(content=result, status=status_code, content_type='application/json')

    def get_operation(self) -> slothql.Operation:
        return get_operation_from_request(self.request)

    def execute_operation(self, operation: slothql.Operation) -> dict:
        return slothql.gql(schema=self.get_schema(), operation=operation)

    def get_query_result(self, operation: slothql.Operation) -> Tuple[Optional[str], int]:
        result = self.execute_operation(operation)
        return self.jsonify(result), 400 if 'errors' in result else 200

    @classmethod
    def jsonify(cls, data: dict) -> str:
        if cls.DEBUG:
            return json.dumps(data, sort_keys=True, indent=2, separators=(',', ': '))
        return json.dumps(data, separators=(',', ':'))

    def get_schema(self):
        return self.DEBUG and self.schema(self.request) if callable(self.schema) else self.schema

    @property
    def show_graphiql(self) -> bool:
        return self.request.content_type in ('text/plain', 'text/html')

    def get_context_data(self) -> OrderedDict:
        return OrderedDict({
            'title': 'GraphiQL',
            'graphiql_version': self.graphiql_version,
        })
