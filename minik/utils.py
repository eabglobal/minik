# -*- coding: utf-8 -*-
"""
    utils.py
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


def create_api_event(resource_path: str, method='POST', **kwargs):
    """
    Create a basic version of the raw API Gateway event a lambda function will
    receive when invoked. The full definition of the event is documented:
    https://docs.aws.amazon.com/lambda/latest/dg/with-on-demand-https.html

    :param resource_path: The path that identifies a route. I.e. /events/{year}/{month}
    :param method: The http method of the event
    """
    path_params = kwargs.get('pathParameters', {})
    path = resource_path
    if path_params:
        path = resource_path.format(**path_params)

    return {
        'requestContext': {
            'httpMethod': method,
            'resourcePath': resource_path,
            'apiId': 'ax2hor23'
        },
        'path': path,
        'resource': resource_path,
        'headers': kwargs.get('headers', {'content-type': 'application/json'}),
        'pathParameters': kwargs.get('pathParameters', {}),
        'queryStringParameters': kwargs.get('queryParameters', {}),
        'body': json.dumps(kwargs.get('body', {})).encode(),
        'stageVariables': kwargs.get('stageVariables', {}),
    }


def create_alb_event(path: str, method='POST', **kwargs):
    """
    Create a basic version of the raw ALB event a lambda function will
    receive when invoked. The full definition of the event is documented:
    https://docs.aws.amazon.com/elasticloadbalancing/latest/application/lambda-functions.html#receive-event-from-load-balancer

    :param path: The path of an ALB request. This is different from the resource path
                  defiend for the API Gateway. I.e. /events/2019/05.
    :param method: The http method of the event
    """

    return {
        "requestContext": {
            "elb": {"targetGroupArn": "arn:aws:some_arn"}
        },
        "httpMethod": method,
        "path": path,
        "queryStringParameters": kwargs.get('queryParameters', {}),
        "headers": kwargs.get('headers', {'content-type': 'application/json'}),
        "body": json.dumps(kwargs.get('body', {})).encode(),
        "isBase64Encoded": kwargs.get('isBase64Encoded', {})
    }
