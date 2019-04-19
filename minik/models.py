import json
from minik.status_codes import codes


class MinikRequest:
    """
    Simple wrapper of the data object received from API Gateway. This object will
    parse a given API gateway event and it will transform it into a more user
    friendly object to operate on. The idea is that a view does not need to be
    concerned with the inner representation of the APIGateway's event as long as
    it has access to the underlaying data values in the event.
    """
    __slots__ = ['path', 'resource', 'query_params', 'headers', 'uri_params',
                 'method', '_body', '_json_body', 'aws_context']

    def __init__(self, path, resource, query_params, headers, uri_params, method, body, context):

        self.path = path
        self.resource = resource
        self.query_params = query_params
        self.headers = headers
        self.uri_params = uri_params
        self.method = method
        self._body = body
        self.aws_context = context
        # The parsed JSON from the body. This value should
        # only be set if the Content-Type header is application/json,
        # which is the default content type.
        self._json_body = None

    @property
    def json_body(self):
        """
        Lazy loading/parsing of the json payload.
        """
        if self.headers.get('content-type', '').startswith('application/json'):
            if self._json_body is None:
                self._json_body = json.loads(self._body)
            return self._json_body


class Response:
    __slots__ = ['body', 'headers', 'status_code']

    def __init__(self, body, headers=None, status_code=codes.ok):
        self.body = body
        self.headers = headers or {}
        self.status_code = status_code

    def to_dict(self, binary_types=None):
        return {
            'headers': self.headers,
            'statusCode': self.status_code,
            'body': self.body
        }


class JsonResponse(Response):
    """
    A very simple wrapper that defines a valid JsonResponse the APIGateway understands.
    The object encapsulates the headers, status code and body of a response.
    """

    def to_dict(self, binary_types=None):

        return {
            'headers': self.headers,
            'statusCode': self.status_code,
            'body': json.dumps(self.body)
        }
