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
import pytest
import requests
from unittest.mock import MagicMock
from minik.constants import CONFIG_ERROR_MSG
from minik.core import Minik, BadRequestError, ConfigurationError, JsonResponse


sample_app = Minik()
context = MagicMock()


@sample_app.route('/activity_no_method')
def no_method_view():
    return {'method': sample_app.current_request.method.lower()}


@sample_app.route('/activity', method='POST')
def post_view():
    return {'id': 2, 'message': 'success'}


@sample_app.route('/activity/{activity_id}', method='GET')
def get_view(activity_id):
    return {'id': activity_id, 'type': 'cycling '}


@pytest.mark.parametrize("http_method", ['POST', 'PUT', 'PATCH', 'DELETE'])
def test_routing_no_method(create_router_event, http_method):
    """
    Validate that if a view is defined without a specific method, ANY http method
    should execute the view.
    """

    event = create_router_event('/activity_no_method',
                                method=http_method,
                                body={'type': 'cycle', 'distance': 15})

    response = sample_app(event, context)
    assert json.loads(response['body'])['method'] == http_method.lower()


def test_routing_for_http_post(create_router_event):
    """
    Validate that a view defined for a POST request is correctly evaluated when
    the route + method match the signature.
    """

    event = create_router_event('/activity',
                                method='POST',
                                body={'type': 'cycle', 'distance': 15})

    response = sample_app(event, context)
    expected_response = post_view()

    assert response['body'] == json.dumps(expected_response)


def test_routing_for_http_get(create_router_event):
    """
    Validate that a view defined for a GET request is correctly evaluated when
    the route + method match the signature.
    """

    activity_id = 152342
    event = create_router_event('/activity/{activity_id}',
                                method='GET',
                                pathParameters={'activity_id': activity_id},
                                body={'type': 'cycle', 'distance': 15})

    response = sample_app(event, context)
    expected_response = get_view(activity_id)

    assert response['body'] == json.dumps(expected_response)