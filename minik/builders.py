from minik.constants import CONFIG_ERROR_MSG

from minik.models import MinikRequest
from minik.exceptions import ConfigurationError


class APIGatewayRequestBuilder:

    def build(self, event, context):

        headers = event.get('headers') or {}

        if 'resource' not in event:
            raise ConfigurationError(CONFIG_ERROR_MSG)

        return MinikRequest(
            path=event['path'],
            resource=event['resource'],
            query_params=event.get('queryStringParameters', {}),
            headers={k.lower(): v for k, v in headers.items()},
            uri_params=event['pathParameters'],
            method=event['requestContext']['httpMethod'],
            body=event['body'],
            context=context
        )


class ALBRequestBuilder:

    def build(self, event, context):

        headers = event.get('headers') or {}

        return MinikRequest(
            path=event['path'],
            resource=None,
            query_params=event.get('queryStringParameters', {}),
            headers={k.lower(): v for k, v in headers.items()},
            uri_params=None,
            method=event['httpMethod'],
            body=event['body'],
            context=context
        )


builders_by_type = {
    'api_request': APIGatewayRequestBuilder(),
    'alb_request': ALBRequestBuilder()
}
