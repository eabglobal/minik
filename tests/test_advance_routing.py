# -*- coding: utf-8 -*-
"""
    test_advance_routing.py
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
from minik.utils import create_api_event

sample_app = Minik()
context = MagicMock()


@sample_app.route("/events/{zip_code}", methods=['GET'])
def get_events(zip_code):
    return {'message': 'get handler'}


@sample_app.route("/events/{zip_code}", methods=['POST'])
def post_event(zip_code):
    return {'message': 'post handler'}


@sample_app.route("/event_list", methods=['GET'])
def get_events_list1():
    return {'message': 'duplicate 1'}


@sample_app.route("/event_list", methods=['GET'])
def get_events_list2():
    return {'message': 'duplicate 2'}


@pytest.mark.parametrize("http_method, expected_message", [
    ('GET', 'get handler'),
    ('POST', 'post handler')
])
def test_route_defined_for_post_put(http_method, expected_message):
    """
    For a given path, minik can execute different routes based on the HTTP method.
    """

    event = create_api_event('/events/{zip_code}',
                                method=http_method,
                                pathParameters={'zip_code': 20902},
                                body={'type': 'cycle'})

    response = sample_app(event, context)

    assert json.loads(response['body'])['message'] == expected_message


def test_route_defined_for_duplicate_views():
    """
    This is an invalid definition in which the user of minik is trying to associate
    two different views for the same (path, method) pair.
    """

    event = create_api_event('/event_list',
                                method='GET',
                                body={'type': 'cycle'})

    response = sample_app(event, context)

    assert response['statusCode'] == codes.not_allowed
