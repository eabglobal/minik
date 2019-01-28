# -*- coding: utf-8 -*-
"""
    conftest.py
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
from pytest import fixture


@fixture
def create_router_event():
    """
    Create an event for the router lambda.
    """
    def create_router_event_inner(uri, method='POST', **kwargs):
        return {
            'requestContext': {
                'httpMethod': method,
                'resourcePath': uri,
            },
            'resource': uri,
            'headers': kwargs.get('headers', {'content-type': 'application/json'}),
            'pathParameters': kwargs.get('pathParameters', {}),
            'queryStringParameters': kwargs.get('queryParameters', {}),
            'body': json.dumps(kwargs.get('body', {})).encode(),
            'stageVariables': {},
        }

    return create_router_event_inner
