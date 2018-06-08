import json

import pytest
from unittest import mock

from django import test

from ..views import GraphQLView

rf = test.RequestFactory()


@pytest.mark.parametrize(
    "value",
    (
        rf.post(path="", data={"query": "query { hello }"}),
        rf.post(
            path="",
            data={
                "query": "query query1 { hello } query query2 { hello }",
                "operationName": "query1",
            },
        ),
    ),
)
def test_query(value, hello_schema):
    response = GraphQLView.as_view(schema=hello_schema)(value)
    assert (200, {"data": {"hello": "world"}}) == (
        response.status_code,
        json.loads(response.content.decode()),
    )


@pytest.mark.parametrize("method", ("options", "put", "patch", "delete", "invalid"))
def test_invalid_method(method, hello_schema):
    response = GraphQLView.as_view(schema=hello_schema)(
        rf.generic(method=method, path="")
    )
    assert (405, b"GraphQL supports only GET and POST requests.") == (
        response.status_code,
        response.content,
    )


@pytest.mark.parametrize(
    "data, message",
    (
        ({"": ""}, {"errors": [{"message": '"query" not found in json object'}]}),
        (
            {"query": "Hello world"},
            {
                "errors": [
                    {
                        "locations": [{"column": 1, "line": 1}],
                        "message": 'Syntax Error GraphQL (1:1) Unexpected Name "Hello"\n'
                        "\n"
                        "1: Hello world\n"
                        "   ^\n",
                    }
                ]
            },
        ),
    ),
)
def test_bad_request(data, message, hello_schema):
    response = GraphQLView.as_view(schema=hello_schema)(rf.post("", data=data))
    assert (400, message) == (
        response.status_code,
        json.loads(response.content.decode()),
    )


@pytest.mark.parametrize("content_type", ("text/html", "text/plain"))
def test_show_graphiql(content_type, hello_schema):
    request = rf.get(path="", content_type=content_type)
    request.content_type = content_type
    with mock.patch.object(
        GraphQLView, "template", render=lambda *_: "<html>hello world</html>"
    ):
        response = GraphQLView.as_view(schema=hello_schema)(request)
    assert (200, b"<html>hello world</html>") == (
        response.status_code,
        response.content,
    )
