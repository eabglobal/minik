# -*- coding: utf-8 -*-
"""
    test_minik.py
    :copyright: © 2019 by the EAB Tech team.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""


import json
from unittest.mock import MagicMock

from minik.status_codes import codes
from minik.constants import CONFIG_ERROR_MSG
from minik.core import Minik, JsonResponse, BadRequestError, ConfigurationError


sample_app = Minik()
context = MagicMock()


@sample_app.route('/findme/{first}/{second}')
def sample_view(first, second):
    return {'sample': 'data', 'values': [51231, 5234]}


@sample_app.route('/bad_request')
def bad_request_view():
    raise BadRequestError('Not good mah friend. Something terrible has happened!')


@sample_app.route('/echo')
def echo_view():
    return sample_app.request.json_body


@sample_app.route('/aws_context')
def aws_ctx_view():
    ctx = sample_app.request.aws_context
    return {
        'aws_request_id': ctx.aws_request_id,
        'log_group_name': ctx.log_group_name,
        'log_stream_name': ctx.log_stream_name
    }


def test_sample_view_with_path_params(create_router_event):

    event = create_router_event('/findme/{first}/{second}',
                                pathParameters={'first': 'adventure', 'second': 'chile'},
                                body={'request_id': 'navigate_request_id', 'urls': '', 'term': ''})

    view_body = sample_view('adventure', 'chile')
    response = sample_app(event, context)

    assert response['body'] == json.dumps(view_body)
    assert response['statusCode'] == codes.ok


def test_sample_view_without_query_params(create_router_event):

    event = create_router_event('/findme/{first}/{second}',
                                pathParameters={'first': 'adventure', 'second': 'chile'},
                                body={'request_id': 'navigate_request_id', 'urls': '', 'term': ''})

    del event['queryStringParameters']
    view_body = sample_view('adventure', 'chile')
    response = sample_app(event, context)

    assert response['body'] == json.dumps(view_body)
    assert response['statusCode'] == codes.ok


def test_sample_view_with_undefined_query_params(create_router_event):

    event = create_router_event('/findme/{first}/{second}',
                                pathParameters={'first': 'adventure', 'second': 'chile'},
                                body={'request_id': 'navigate_request_id', 'urls': '', 'term': ''})

    event['queryStringParameters'] = None
    view_body = sample_view('adventure', 'chile')
    response = sample_app(event, context)

    assert response['body'] == json.dumps(view_body)
    assert response['statusCode'] == codes.ok


def test_sample_view_without_headers(create_router_event):

    event = create_router_event('/findme/{first}/{second}',
                                pathParameters={'first': 'adventure', 'second': 'chile'},
                                body={'request_id': 'navigate_request_id', 'urls': '', 'term': ''})

    del event['headers']
    response = sample_app(event, context)

    assert response['statusCode'] == codes.ok


def test_sample_view_with_undefined_headers(create_router_event):

    event = create_router_event('/findme/{first}/{second}',
                                pathParameters={'first': 'adventure', 'second': 'chile'},
                                body={'request_id': 'navigate_request_id', 'urls': '', 'term': ''})

    event['headers'] = None
    response = sample_app(event, context)

    assert response['statusCode'] == codes.ok


def test_sample_view_route_does_not_match(create_router_event):

    event = create_router_event('/router/mismatch',
                                pathParameters={'first': 'adventure'},
                                body={'request_id': 'navigate_request_id', 'urls': '', 'term': ''})

    response = sample_app(event, context)

    assert response['statusCode'] == codes.not_found


def test_bad_request_correctly_handled(create_router_event):

    event = create_router_event('/bad_request', body={'sample': 'field'})

    response = sample_app(event, context)

    assert response['statusCode'] == codes.bad_request
    assert 'Not good mah friend. Something terrible has happened!' in response['body']


def test_json_body_in_view(create_router_event):
    """
    Test that a given view has access to the request.json_body. The current
    request contains the data of the requests payload.
    """

    test_body = {'field': 'value', 'expected': [2, 3, 4, 5]}
    event = create_router_event('/echo', body=test_body)

    response = sample_app(event, context)

    assert response['statusCode'] == codes.ok
    assert json.loads(response['body']) == test_body


def test_view_without_path_parameters(create_router_event):
    """
    Validate that a view without uri paramters does not crash when invoked.
    """

    test_body = {'field': 'value', 'expected': [2, 3, 4, 5]}
    event = create_router_event('/echo', body=test_body, pathParameters=None)

    response = sample_app(event, context)

    assert response['statusCode'] == codes.ok
    assert json.loads(response['body']) == test_body


def test_event_without_resoure_raises_error(create_router_event):
    """
    This is a misconfiguration in the integration between the API gateway and the
    lambda function. If the uri is None, that means that the event is not being
    correctly propagated to the lambda function.
    """

    test_body = {'field': 'value', 'expected': [2, 3, 4, 5]}
    event = create_router_event('/echo', body=test_body)
    del event['resource']

    try:
        sample_app(event, context)
    except ConfigurationError as ce:
        assert CONFIG_ERROR_MSG in str(ce)


def test_correctly_pass_aws_context_to_request(create_router_event):
    """
    This is a misconfiguration in the integration between the API gateway and the
    lambda function. If the uri is None, that means that the event is not being
    correctly propagated to the lambda function.
    """

    test_body = {'field': 'value', 'expected': [2, 3, 4, 5]}
    event = create_router_event('/aws_context', body=test_body)

    context.aws_request_id = 'aws_request_id_123'
    context.log_group_name = 'log_group_name_123'
    context.log_stream_name = 'log_stream_name_123'

    response = sample_app(event, context)
    response_body = json.loads(response['body'])

    for key in response_body:
        assert response_body[key] == getattr(context, key)


def test_response_headers():
    """
    This test validates that the default value given to the headers of the json
    response does NOT have a default value. A default of a mutable object is
    shared across instances.
    """

    # No headers are passed in
    response1 = JsonResponse('sample body')
    response1.headers['findme'] = 'Instance 1'

    response2 = JsonResponse('other body')

    assert response1.headers != response2.headers
    assert 'findme' not in response2.headers
