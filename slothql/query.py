from typing import List, Tuple, Any, Optional

from graphql import Source, parse, validate, GraphQLSchema
from graphql.error import format_error, GraphQLSyntaxError
from graphql import execute

import slothql


class ExecutionResult(dict):
    @property
    def invalid(self) -> bool:
        return bool(self.get('errors'))

    @property
    def errors(self) -> Optional[list]:
        return self.get('errors', [])

    @property
    def data(self):
        return self.get('data')


class Query:
    __slots__ = 'query', 'schema', 'ast', 'errors'

    def __init__(self, query: str, schema: slothql.Schema):
        assert isinstance(query, str), f'Expected query string, got {query}'
        assert isinstance(schema, GraphQLSchema), f'schema has to be of type Schema, not {schema}'

        self.query, self.schema = query, schema
        self.ast, self.errors = self.get_ast(self.query, self.schema)

    @classmethod
    def get_ast(cls, query, schema) -> Tuple[Any, List[GraphQLSyntaxError]]:
        try:
            ast = parse(Source(query))
        except GraphQLSyntaxError as e:
            return None, [e]
        return ast, validate(schema, ast)

    def execute(self) -> ExecutionResult:
        if self.errors:
            return ExecutionResult(errors=[self.format_error(e) for e in self.errors])
        return ExecutionResult(data=execute(self.schema, self.ast).data)

    @classmethod
    def format_error(cls, error: Exception) -> dict:
        if isinstance(error, GraphQLSyntaxError):
            return format_error(error)
        return {'message': str(error)}


def gql(schema: slothql.Schema, query: str) -> ExecutionResult:
    return Query(query, schema).execute()
