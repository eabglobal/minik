# -*- coding: utf-8 -*-
"""
    test_routing_decorators.py
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


sample_app = Minik()
context = MagicMock()


@sample_app.route('/activity_no_method')
def no_method_view():
    return {'method': sample_app.request.method.lower()}


@sample_app.post('/activity')
def post_view():
    return {'id': 2, 'message': 'success'}


@sample_app.get('/activity/{activity_id}', validators=[True])
def get_view(activity_id: int):
    return {'id': activity_id, 'type': 'cycling '}


@sample_app.put('/activity/{activity_id}')
def put_view(activity_id: int):
    return {'updated': True}


@sample_app.delete('/activity/{activity_id}')
def delete_view(activity_id: int):
    return {'removed': True}


def test_routing_for_http_post(create_router_event):

    event = create_router_event('/activity',
                                method='POST',
                                body={'type': 'cycle', 'distance': 15})

    response = sample_app(event, context)
    expected_response = post_view()

    assert response['body'] == json.dumps(expected_response)


@pytest.mark.parametrize("http_method, expected_response", [
    ('GET', get_view(123)),
    ('PUT', put_view(123)),
    ('DELETE', delete_view(123)),
])
def test_routing_for_http_get(create_router_event, http_method, expected_response):
    """
    Validate that a view defined for a GET request is correctly evaluated when
    the route + method match the signature.
    """

    event = create_router_event('/activity/{activity_id}',
                                method=http_method,
                                pathParameters={'activity_id': 123})

    response = sample_app(event, context)

    assert response['body'] == json.dumps(expected_response)
