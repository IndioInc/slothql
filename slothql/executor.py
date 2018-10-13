import typing as t

import graphql
from graphql.execution import ExecutionResult
from graphql.execution.executor import execute_operation
from graphql.execution.executors.sync import SyncExecutor
from graphql.execution.utils import ExecutionContext
from graphql.language.ast import Document


class Executor(SyncExecutor):
    def __init__(self):
        super().__init__()
        self.error: t.Optional[Exception] = None

    def execute(self, fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            self.error = e


def execute(
    schema: graphql.GraphQLSchema,
    document_ast: Document,
    variables=None,
    operation_name: str = None,
) -> ExecutionResult:
    exe_context = ExecutionContext(
        schema=schema,
        document_ast=document_ast,
        root_value=None,
        context_value=None,
        variable_values=variables or {},
        operation_name=operation_name,
        executor=Executor(),
        middleware=None,
        allow_subscriptions=False,
    )

    data = execute_operation(exe_context, exe_context.operation, exe_context.root_value)
    if exe_context.executor.error:
        raise exe_context.executor.error
    return ExecutionResult(data=data)
