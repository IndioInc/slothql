import json

import pytest

from django.test import RequestFactory

from ..views import GraphQLView

rf = RequestFactory()


def test_query(hello_schema):
    request = rf.post(path='', data={'query': 'query { hello }'})
    response = GraphQLView.as_view(schema=hello_schema)(request)
    assert (200, {'data': {'hello': 'world'}}) == (
        response.status_code, json.loads(response.content.decode())
    )


@pytest.mark.parametrize('method', ('options', 'put', 'patch', 'delete', 'invalid'))
def test_invalid_method(method, hello_schema):
    response = GraphQLView.as_view(schema=hello_schema)(rf.generic(method=method, path=''))
    assert (405, b'GraphQL supports only GET and POST requests.') == (
        response.status_code, response.content
    )


@pytest.mark.parametrize(
    'data, message',
    (
        ({'': ''}, {'errors': [{'message': '"query" not found in json object'}]}),
        (
            {'query': 'Hello world'},
            {
                'errors': [
                    {
                        'locations': [{'column': 1, 'line': 1}],
                        'message': 'Syntax Error GraphQL (1:1) Unexpected Name "Hello"\n'
                        '\n'
                        '1: Hello world\n'
                        '   ^\n',
                    }
                ]
            },
        ),
    ),
)
def test_bad_request(data, message, hello_schema):
    response = GraphQLView.as_view(schema=hello_schema)(rf.post('', data=data))
    assert (400, message) == (
        response.status_code, json.loads(response.content.decode())
    )


@pytest.mark.skip
@pytest.mark.parametrize('content_type', ('text/html', 'text/plain'))
def test_show_graphiql(content_type):
    request = rf.get(path='')
