# -*- coding: utf-8 -*-
"""
    test_alb_support.py
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
from unittest.mock import MagicMock
from minik.core import Minik
from minik.status_codes import codes


sample_app = Minik()
context = MagicMock()


@sample_app.get("/events/{zip_code}")
def get_events(zip_code):
    return {'message': 'get handler'}


@sample_app.post("/events/{zip_code}")
def post_event(zip_code):
    return {'message': 'post handler'}


@sample_app.route("/echo")
def echo_handler():
    return {'req_ctx': sample_app.request.aws_event['requestContext']}


@pytest.mark.parametrize("http_method, expected_message", [
    ('GET', 'get handler'),
    ('POST', 'post handler')
])
def test_route_defined_for_post_put(create_alb_event, http_method, expected_message):
    """
    For a given path, minik can execute different routes based on the HTTP method.
    """

    event = create_alb_event('/events/20902',
                             method=http_method,
                             body={'type': 'cycle'})

    response = sample_app(event, context)

    assert json.loads(response['body'])['message'] == expected_message


@pytest.mark.parametrize("http_method", [
    'GET', 'POST', 'PUT', 'DELETE'
])
def test_access_to_source_event(create_alb_event, http_method):
    """
    Validate that a view has access to the raw event minik received independent
    of the method type.
    """

    event = create_alb_event('/echo',
                             method=http_method,
                             body={'type': 'cycle'})

    response = sample_app(event, context)
    json_response_body = json.loads(response['body'])

    assert json_response_body['req_ctx'] == event['requestContext']
