# -*- coding: utf-8 -*-
"""
    builders.py
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

import urllib.parse
from minik.constants import CONFIG_ERROR_MSG

from minik.models import MinikRequest
from minik.exceptions import MinikViewError, ConfigurationError


class APIGatewayRequestBuilder:
    """
    This builder knows how to convert an API Gateway event into a MinikRequest instance.
    The event should be the payload a lambda function receives when it is the target
    of a gateway endpoint. The payload definition is:
    https://docs.aws.amazon.com/lambda/latest/dg/with-on-demand-https.html
    """

    def matches(self, event):
        """
        A simple function to determine if the given raw event comes from the API
        Gateway. If it is, then the function evaluates to True, False otherwise.

        :param event: The raw event received from the lambda function.
        """
        return event.get('requestContext', {}).get('apiId') is not None

    def build(self, event, context, router):
        """
        Map the raw API Gateway event to a MinikRequest.

        :param event: The raw lambda function event.
        :param context: The raw lambda function context object.
        :param router: An instance of the minik router.
        """

        headers = event.get('headers') or {}

        if 'resource' not in event:
            raise ConfigurationError(CONFIG_ERROR_MSG)

        return MinikRequest(
            request_type='api_request',
            path=event['path'],
            resource=event['resource'],
            query_params=event.get('queryStringParameters') or {},
            headers={k.lower(): v for k, v in headers.items()},
            uri_params=event['pathParameters'] or {},
            method=event['requestContext']['httpMethod'],
            body=event['body'],
            context=context,
            event=event
        )


class ALBRequestBuilder:
    """
    This request builder knows how to convert an ALB event to a MinikRequest instance.
    The ALB event is the payload a lambda function receives, when it is the target
    of an application load balancer.

    https://docs.aws.amazon.com/lambda/latest/dg/services-alb.html
    """

    def matches(self, event):
        """
        A simple function to determine if the given raw event comes from the AWS
        Application Load Balancer (ALB). If it is, then the function evaluates
        to True, False otherwise.

        :param event: The raw event received from the lambda function.
        """
        return event.get('requestContext', {}).get('elb') is not None

    def build(self, event, context, router):
        """
        Map the ALB raw request to a MinikRequest instance. As part of the mapping
        the router will be used to convert the raw request path into a resource.
        A path, as defined in the event, looks like '/books/2019', the mapping will
        look up the associated resource '/books/{year}' from the router and correctly
        build a MinikRequest instance.

        :param event: The raw lambda function event.
        :param context: The raw lambda function context object.
        :param router: An instance of the minik router.
        """

        headers = event.get('headers') or {}
        resource, uri_params = router.resolve_path(event['path'])

        return MinikRequest(
            request_type='alb_request',
            path=event['path'],
            resource=resource,
            query_params=url_decode_params(event.get('queryStringParameters') or {}),
            headers={k.lower(): v for k, v in headers.items()},
            uri_params=uri_params,
            method=event['httpMethod'],
            body=event['body'],
            context=context,
            event=event
        )


def url_decode_params(query_params):
    """
    Decode the key value pairs of a set of parameters.
    """

    def _decode_string(key_or_value):
        """
        Use unquote_plus first to convert + into spaces. Then use unquote to decode any other encodings.
        """
        return urllib.parse.unquote(urllib.parse.unquote_plus(key_or_value))

    return {
        _decode_string(key): _decode_string(value)
        for key, value in query_params.items()
    }


REQUEST_BUILDERS = [
    APIGatewayRequestBuilder(),
    ALBRequestBuilder()
]


def build_request(event, context, router):
    """
    Build a minik request from the given lambda function event. Given a set of
    supported builders, the raw event will be mapped based on the event type. If
    the type of event is not supported, an exception will be raised.

    :param event: The raw event received by the lambda function.
    :param context: The raw context objects of the lambda function
    :param router: An instance of the minik router.
    """

    for builder in REQUEST_BUILDERS:
        if builder.matches(event):
            return builder.build(event, context, router)

    raise MinikViewError('Unsupported event type.')
