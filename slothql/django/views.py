import json
from collections import OrderedDict
from typing import Tuple, Optional, Union, Callable

from cached_property import cached_property
from django import template
from django.core.handlers.wsgi import WSGIRequest
from django.views import View
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse

from graphql.type.schema import GraphQLSchema

import slothql
from slothql.template import get_template_string

from .utils.request import get_operation_from_request


class GraphQLView(View):
    DEBUG = True
    allowed_methods = ("GET", "POST")

    graphiql_version: str = "0.11.10"
    graphiql_template: str = "graphiql.html"

    schema: Union[GraphQLSchema, Callable] = None

    @classmethod
    def as_view(cls, **initkwargs):
        schema = initkwargs.get("schema")
        assert (
            schema is not None
        ), f"Expected schema to be of type Schema, but got {schema}"
        return super().as_view(**initkwargs)

    def dispatch(self, request: WSGIRequest, *args, **kwargs) -> HttpResponse:
        if request.method not in self.allowed_methods:
            return HttpResponseNotAllowed(
                ["GET", "POST"], "GraphQL supports only GET and POST requests."
            )

        query, parse_error = self.get_operation()

        result, status_code = self.get_query_result(query)
        if self.show_graphiql:
            context = template.Context(
                {**self.get_context_data(), **{"result": result if query else ""}}
            )
            return HttpResponse(
                self.template.render(context), status=status_code if query else 200
            )

        if parse_error:
            return JsonResponse({"errors": [{"message": parse_error}]}, status=400)
        return HttpResponse(
            content=result, status=status_code, content_type="application/json"
        )

    @cached_property
    def template(self) -> template.Template:
        return template.Template(get_template_string(self.graphiql_template))

    def get_operation(self) -> Tuple[Optional[slothql.Operation], Optional[str]]:
        try:
            return get_operation_from_request(self.request), None
        except slothql.InvalidOperation as e:
            return None, str(e)

    def execute_operation(
        self, operation: slothql.Operation
    ) -> slothql.ExecutionResult:
        return slothql.gql(schema=self.get_schema(), operation=operation)

    def get_query_result(
        self, operation: slothql.Operation = None
    ) -> Tuple[Optional[str], int]:
        if operation:
            result = self.execute_operation(operation)
            return self.jsonify(result), 200 if result.valid else 400
        return None, 400

    @classmethod
    def jsonify(cls, data: dict) -> str:
        if cls.DEBUG:
            return json.dumps(data, sort_keys=True, indent=2, separators=(",", ": "))
        return json.dumps(data, separators=(",", ":"))

    def get_schema(self):
        return (
            self.DEBUG and self.schema(self.request)
            if callable(self.schema)
            else self.schema
        )

    @property
    def show_graphiql(self) -> bool:
        return self.request.method == "GET" and self.request.content_type in (
            "text/plain",
            "text/html",
        )

    def get_context_data(self) -> OrderedDict:
        return OrderedDict(
            {"title": "GraphiQL", "graphiql_version": self.graphiql_version}
        )
