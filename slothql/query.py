import typing as t

from graphql import Source, parse, validate, GraphQLSchema
from graphql.error import format_error, GraphQLSyntaxError

from .executor import execute

import slothql


class ExecutionResult(dict):
    @property
    def errors(self) -> t.Optional[list]:
        return self.get("errors", [])

    @property
    def data(self):
        return self.get("data")

    @property
    def valid(self) -> bool:
        return "errors" not in self


class Query:
    __slots__ = "schema", "operation", "ast", "errors"

    def __init__(self, schema: slothql.Schema, operation: slothql.Operation):
        assert isinstance(
            operation.query, str
        ), f"Expected query string, got {operation.query}"
        assert isinstance(
            schema, GraphQLSchema
        ), f"schema has to be of type Schema, not {schema}"

        self.schema, self.operation = schema, operation
        self.ast, self.errors = self.get_ast(self.operation.query, self.schema)

    @classmethod
    def get_ast(cls, query, schema) -> t.Tuple[t.Any, t.List[GraphQLSyntaxError]]:
        try:
            ast = parse(Source(query))
        except GraphQLSyntaxError as e:
            return None, [e]
        return ast, validate(schema, ast)

    def execute(self) -> ExecutionResult:
        if self.errors:
            return ExecutionResult(errors=[self.format_error(e) for e in self.errors])

        result = execute(
            schema=self.schema,
            document_ast=self.ast,
            variables=self.operation.variables,
            operation_name=self.operation.operation_name,
        )

        return ExecutionResult(data=result.data)

    @classmethod
    def format_error(cls, error: Exception) -> dict:
        if isinstance(error, GraphQLSyntaxError):
            return format_error(error)
        return {"message": str(error)}


def gql(
    schema: slothql.Schema,
    query: str = None,
    *,
    variables: dict = None,
    operation_name: str = None,
    operation: slothql.Operation = None,
) -> ExecutionResult:
    if operation:
        assert not query, 'Using "query" with "operation" is ambiguous'
        assert not variables, 'Using "variables" with "operation" is ambiguous'
        assert (
            not operation_name
        ), 'Using "operation_name" with "operation" is ambiguous'
    else:
        operation = slothql.Operation(
            query=query, variables=variables, operation_name=operation_name
        )

    return Query(schema, operation).execute()
