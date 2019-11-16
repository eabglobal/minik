# -*- coding: utf-8 -*-
"""
    test_route_validation.py
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
import uuid
from unittest.mock import MagicMock

from minik.core import Minik
from minik.fields import ReStr, BaseRouteField
from minik.status_codes import codes
from minik.utils import create_api_event


sample_app = Minik()
context = MagicMock()


@sample_app.route('/bio/{username}', methods=['GET'])
def get_re_view(username: str):
    return {'user': username}


@pytest.mark.parametrize("username", [('busthead'), ('123'), ('pd_az'), ('hello-world')])
def test_str_route_validation_valid(username):
    """
    The string based route validation will match any valid \w+ regular expression,
    which is used for unicode patterns [a-zA-Z0-9_].

    https://docs.python.org/3/library/re.html
    """

    event = create_api_event('/bio/{username}',
                                method='GET',
                                pathParameters={'username': username})

    response = sample_app(event, context)
    expected_response = get_re_view(username)

    assert response['body'] == json.dumps(expected_response)


@pytest.mark.parametrize("username", [('$$$'), ('12#3'), ('hello@gmail')])
def test_str_route_validation_invalid(username):
    """
    Test string based routing with INVALID paramters. Note that partial matches
    will be rejected. For instance hello@gmail will be rejected given that `@`
    is not part of [a-zA-Z0-9_] pattern.
    """

    event = create_api_event('/bio/{username}',
                                method='GET',
                                pathParameters={'username': username})

    response = sample_app(event, context)
    assert response['statusCode'] == codes.not_found


@sample_app.route('/articles/{year}/{month}/', methods=['GET'])
def get_articles_view(year: int, month: int):
    # Make sure that the year and month are integers!
    assert isinstance(year, int) and isinstance(month, int)
    return {'year': year, 'month': month}


def test_route_with_int_valid():

    event = create_api_event('/articles/{year}/{month}/',
                                method='GET',
                                pathParameters={'year': '2020', 'month': '10'})

    response = sample_app(event, context)
    expected_response = get_articles_view(2020, 10)

    assert response['body'] == json.dumps(expected_response)


@pytest.mark.parametrize("year,month", [
    ('2020', 'INVALID'), ('INVALID', '12'), ('hello', 'world'),
])
def test_route_with_int_invalid_params(year, month):

    event = create_api_event('/articles/{year}/{month}/',
                                method='GET',
                                pathParameters={'year': year, 'month': month})

    response = sample_app(event, context)
    assert response['statusCode'] == codes.not_found


@sample_app.route('/product/{product_id}/', methods=['GET'])
def get_product(product_id: uuid.UUID):
    assert isinstance(product_id, uuid.UUID)
    return {'id': str(product_id)}


def test_uuid_in_route_valid():
    """
    Validate a uuid based parameter with a valid value.
    """

    pid = '00010203-0405-0607-0809-0a0b0c0d0e0f'
    event = create_api_event('/product/{product_id}/',
                                method='GET',
                                pathParameters={'product_id': pid})

    response = sample_app(event, context)

    assert json.loads(response['body'])['id'] == pid


@pytest.mark.parametrize("product_id", [
    ('00010203-0405-0607-0809'),
    ('INVALID'),
])
def test_uuid_in_route_invalid(product_id):
    """
    Validate the uiid based view with invalid values.
    """

    event = create_api_event('/product/{product_id}/',
                                method='GET',
                                pathParameters={'product_id': product_id})

    response = sample_app(event, context)
    assert response['statusCode'] == codes.not_found


@sample_app.route('/item/{item_id}/', methods=['GET'])
def get_item(item_id: ReStr(r'([0-9a-f]{8}$)')):
    assert isinstance(item_id, str)
    return {'id': item_id}


@pytest.mark.parametrize("item_id", [
    ('00010203'), ('52342512'), ('00102c03')
])
def test_custom_re_in_route_valid(item_id):
    """
    Validate a uuid based parameter with a valid value.
    """

    event = create_api_event('/item/{item_id}/',
                                method='GET',
                                pathParameters={'item_id': item_id})

    response = sample_app(event, context)

    assert json.loads(response['body'])['id'] == item_id


@pytest.mark.parametrize("item_id", [
    ('04052523209'), ('060809'), ('#0010203'), ('00102i03')
])
def test_custom_re_in_route_invalid(item_id):
    """
    Validate the uiid based view with invalid values.
    """

    event = create_api_event('/item/{item_id}/',
                                method='GET',
                                pathParameters={'item_id': item_id})

    response = sample_app(event, context)
    assert response['statusCode'] == codes.not_found


class RouteTracker(BaseRouteField):

    def validate(self, value):
        return value in ('fitbit', 'nikeplus', 'vivosmart',)


@sample_app.route('/tracker/{name}/', methods=['GET'])
def get_tracker_info(name: RouteTracker):
    assert isinstance(name, str)
    return {'name': name}


@pytest.mark.parametrize("tracker_name", [
    ('fitbit'), ('nikeplus'), ('vivosmart')
])
def test_custom_field_in_route_valid(tracker_name):
    """
    Validate that a route with a custom field definition works when valid values
    are provided.
    """

    event = create_api_event('/tracker/{name}/',
                                method='GET',
                                pathParameters={'name': tracker_name})

    response = sample_app(event, context)

    assert json.loads(response['body'])['name'] == tracker_name


@pytest.mark.parametrize("tracker_name", [
    ('not there'), ('other')
])
def test_custom_field_in_route_invalid(tracker_name):
    """
    Custom route field with invalid values.
    """

    event = create_api_event('/tracker/{name}/',
                                method='GET',
                                pathParameters={'name': tracker_name})

    response = sample_app(event, context)
    assert response['statusCode'] == codes.not_found
