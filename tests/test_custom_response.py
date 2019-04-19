# -*- coding: utf-8 -*-
"""
    test_custom_response.py
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
from minik.models import Response
from minik.status_codes import codes


sample_app = Minik()
context = MagicMock()


@sample_app.get("/events/{zip_code}")
def get_events(zip_code: int):
    return Response(
        headers={'Content-Type': 'text/html'},
        body='hello')


@sample_app.post("/events/{zip_code}")
def post_event(zip_code: int):
    return Response(
        status_code=codes.partial,
        headers={'Content-Type': 'application/json'},
        body=json.dumps({'findme': True, 'zip': zip_code})
    )


def test_get_custom_response(create_router_event):

    event = create_router_event('/events/{zip_code}',
                                method='GET',
                                pathParameters={'zip_code': 20902})

    expected = get_events(20902)
    response = sample_app(event, context)

    assert response['body'] == expected.body
    assert response['headers'] == expected.headers
    assert response['statusCode'] == expected.status_code


def test_post_custom_response(create_router_event):

    event = create_router_event('/events/{zip_code}',
                                method='POST',
                                pathParameters={'zip_code': 20902})

    expected = post_event(20902)
    response = sample_app(event, context)

    assert response['body'] == expected.body
    assert response['headers'] == expected.headers
    assert response['statusCode'] == expected.status_code
