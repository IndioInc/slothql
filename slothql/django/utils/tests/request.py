import json
from urllib.parse import urlencode

import pytest
from unittest import mock

from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory

from ..request import get_operation_from_request

query = 'query { hello }'
rf = RequestFactory()


@pytest.mark.parametrize('value', (
        rf.get('', data={'query': query}),
        rf.post('', data=json.dumps({'query': query}), content_type='multipart/form-data'),
        rf.post('', data=urlencode({'query': query}), content_type='application/x-www-form-urlencoded'),
        rf.post('', data=json.dumps({'query': query}), content_type='application/graphql'),
        rf.post('', data=json.dumps({'query': query}), content_type='application/json'),
))
def test_query_from_request__get(value: WSGIRequest):
    assert query == get_operation_from_request(value).query


def test_query_from_request__post_no_content_type():
    with pytest.raises(ValidationError) as exc_info:
        assert query == get_operation_from_request(rf.post('', data={'query': query}, content_type='')).query
    assert 'content-type not specified' in str(exc_info.value)


@pytest.mark.parametrize('content_type', (
        'text/html',
))
def test_query_from_request__post_unsupported(content_type):
    with pytest.raises(ValidationError) as exc_info:
        assert query == get_operation_from_request(rf.post('', data={'query': query}, content_type=content_type)).query
    assert f'Unsupported content-type {content_type}' in str(exc_info.value)


@mock.patch('slothql.operation.from_raw_json', side_effect=ValueError('mocked exception'))
def test_query_from_request__post_invalid_json(from_raw_json):
    with pytest.raises(ValidationError) as exc_info:
        get_operation_from_request(rf.post('', data='{"query": "hello"}', content_type='application/json'))
    assert 'mocked exception' in str(exc_info.value)
