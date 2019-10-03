from minik.constants import CONFIG_ERROR_MSG

from minik.models import MinikRequest
from minik.exceptions import MinikViewError, ConfigurationError


class APIGatewayRequestBuilder:

    def matches(self, event):
        return event.get('requestContext', {}).get('apiId') is not None

    def build(self, event, context, router):

        headers = event.get('headers') or {}

        if 'resource' not in event:
            raise ConfigurationError(CONFIG_ERROR_MSG)

        return MinikRequest(
            request_type='api_request',
            path=event['path'],
            resource=event['resource'],
            query_params=event.get('queryStringParameters', {}),
            headers={k.lower(): v for k, v in headers.items()},
            uri_params=event['pathParameters'] or {},
            method=event['requestContext']['httpMethod'],
            body=event['body'],
            context=context
        )


class ALBRequestBuilder:

    def matches(self, event):
        return event.get('requestContext', {}).get('elb') is not None

    def build(self, event, context, router):

        headers = event.get('headers') or {}
        resource, uri_params = router.resolve_path(event['path'])

        return MinikRequest(
            request_type='alb_request',
            path=event['path'],
            resource=resource,
            query_params=event.get('queryStringParameters', {}),
            headers={k.lower(): v for k, v in headers.items()},
            uri_params=uri_params,
            method=event['httpMethod'],
            body=event['body'],
            context=context
        )


REQUEST_BUILDERS = [
    APIGatewayRequestBuilder(),
    ALBRequestBuilder()
]


def build_request(event, context, router):

    for builder in REQUEST_BUILDERS:
        if builder.matches(event):
            return builder.build(event, context, router)

    raise MinikViewError('Unsupported event type.')
