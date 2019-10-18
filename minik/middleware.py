import traceback
import json

from minik.constants import DEFAULT_500_ERROR
from minik.status_codes import codes


class ServerErrorMiddleware:
    """
    Handler for a caught server error. The minikexception caught will have the
    status code that should be given to the response as well as the error message.
    These parameters will be used to update the response of a given request.
    """

    def __call__(self, app, error, *args, **kwargs):
        """
        Execute the middleware and update the response object based on the values
        of the request.

        :param app: The instance of the minik app.
        :param error: The instance of the MinikError.
        """
        app.response.status_code = error.status_code
        app.response.body = {'error_message': str(error)}


class ExceptionMiddleware:
    """
    Middleware used to trace unhandled exceptions. This middleware will update
    the response of the current request to reflect the reason of failure.
    """

    def __call__(self, app, error, *args, **kwargs):
        """
        Execute the middleware for the given request with an exception instance.
        If the app is in debug mode, the message will be reflected in the response
        body, otherwise, a generic response is returned.

        :param app: The instance of the minik app.
        :param error: The unhandled exception.
        """

        body = _trace_error(error)

        app.response.status_code = codes.server_error
        app.response.body = body if app.in_debug else DEFAULT_500_ERROR


class ContentTypeMiddleware:
    """
    Update the response body based on the content type of the current response.
    """
    _transformer_by_content_type = {
        'application/json': lambda body: json.dumps(body)
    }

    def __call__(self, app, *args, **kwargs):
        """
        Execute the middleware for the given request, if the content type of the
        response has an additional converter, update the body of the response with
        the appropriate value.

        :param app: The instance of the minik app.
        """

        transformer = self._transformer_by_content_type.get(app.response.content_type, _no_op_transform)
        app.response.body = transformer(app.response.body)


def _no_op_transform(body):
    return body


def _trace_error(te):

    tracer = ''.join(traceback.format_exc())
    body = {'error_message': str(te), 'trace': tracer}
    print(body)
    return body
