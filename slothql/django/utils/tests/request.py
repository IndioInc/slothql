import json
from urllib.parse import urlencode

import pytest
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import RequestFactory

from ..request import get_query_from_request

query = 'query { hello }'
rf = RequestFactory()


def test_query_from_request__get():
    assert get_query_from_request(rf.get('', data={'query': query})) == query


def test_query_from_request__post_x_www_form_url_encoded():
    content_type = 'application/x-www-form-urlencoded'
    assert query == get_query_from_request(rf.post('', data=urlencode({'query': query}), content_type=content_type))


def test_query_from_request__post_multipart():
    assert query == get_query_from_request(rf.post('', data={'query': query}))


def test_query_from_request__post_no_content_type():
    with pytest.raises(ValidationError) as exc_info:
        assert query == get_query_from_request(rf.post('', data={'query': query}, content_type=''))
    assert 'content-type not specified' in str(exc_info.value)


def test_query_from_request__post_unsupported():
    with pytest.raises(ValidationError) as exc_info:
        assert query == get_query_from_request(rf.post('', data={'query': query}, content_type='text/html'))
    assert 'Unsupported content-type text/html' in str(exc_info.value)


def test_query_from_request__post_graphql():
    assert query == get_query_from_request(rf.post('', data=query, content_type='application/graphql'))


def test_query_from_request__post_json():
    assert get_query_from_request(rf.post('', data=json.dumps({'query': query}), content_type='application/json'))


@mock.patch('slothql.utils.query_from_raw_json', side_effect=ValueError('mocked exception'))
def test_query_from_request__post_invalid_json(query_from_raw_json):
    with pytest.raises(ValidationError) as exc_info:
        get_query_from_request(rf.post('', data='{"query": "hello"}', content_type='application/json'))
    assert 'mocked exception' in str(exc_info.value)
