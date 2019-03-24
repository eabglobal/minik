# -*- coding: utf-8 -*-
"""
    test_routing.py
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
from minik.exceptions import MinikViewError
from minik.validators import ReValidator
from minik.status_codes import codes


sample_app = Minik()
context = MagicMock()


@sample_app.route('/bio/{username}', methods=['GET'], validator=ReValidator(r'/bio/(?P<username>\w+)'))
def get_re_view(username):
    return {'user': username}


def test_regex_based_routing_valid_match(create_router_event):
    """
    Validate that a view defined for a GET request is correctly evaluated when
    the route + method match the signature.
    """

    event = create_router_event('/bio/{username}',
                                method='GET',
                                pathParameters={'username': 'busthead'})

    response = sample_app(event, context)
    expected_response = get_re_view('busthead')

    assert response['body'] == json.dumps(expected_response)


def test_regex_based_routing_invalid_match(create_router_event):
    """
    Validate that a view defined for a GET request is correctly evaluated when
    the route + method match the signature.
    """

    event = create_router_event('/bio/{username}',
                                method='GET',
                                pathParameters={'username': '$$$'})

    try:
        sample_app(event, context)
    except MinikViewError as mve:
        assert mve.status_code == codes.not_found


@sample_app.route('/articles/{year}/{month}/', methods=['GET'], validator=ReValidator(r'/articles/(\d+)/(\d{1,2})/'))
def get_articles_view(year, month):
    return {'year': year, 'month': month}


def test_complex_regex_based_routing_valid_match(create_router_event):

    event = create_router_event('/articles/{year}/{month}/',
                                method='GET',
                                pathParameters={'year': '2020', 'month': '10'})

    response = sample_app(event, context)
    expected_response = get_articles_view('2020', '10')

    assert response['body'] == json.dumps(expected_response)


@pytest.mark.parametrize("year,month", [
    ('2020', '120'),
    ('2020', 'INVALID'),
    ('INVALID', '12'),
    ('hello', 'world'),
])
def test_complex_regex_based_routing_invalid_match(create_router_event, year, month):

    event = create_router_event('/articles/{year}/{month}/',
                                method='GET',
                                pathParameters={'year': year, 'month': month})

    try:
        sample_app(event, context)
    except MinikViewError as mve:
        assert mve.status_code == codes.not_found
