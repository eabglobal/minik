from minik.constants import CONFIG_ERROR_MSG

from minik.models import MinikRequest
from minik.exceptions import ConfigurationError


class APIGatewayRequestBuilder:

    def build(self, event, context):

        headers = self._get_with_default(event, 'headers')

        if 'resource' not in event:
            raise ConfigurationError(CONFIG_ERROR_MSG)

        return MinikRequest(
            path=event['path'],
            resource=event['resource'],
            query_params=self._get_with_default(event, 'queryStringParameters'),
            headers={k.lower(): v for k, v in headers.items()},
            uri_params=event['pathParameters'],
            method=event['requestContext']['httpMethod'],
            body=event['body'],
            context=context
        )

    def _get_with_default(self, event, param_name, default={}):
        return event.get(param_name, {}) or default
