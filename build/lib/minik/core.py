# -*- coding: utf-8 -*-
"""
    core.py
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
import traceback
from collections import namedtuple, defaultdict
from minik.constants import CONFIG_ERROR_MSG
from minik.status_codes import codes

SimpleRoute = namedtuple('SimpleRoute', ['view', 'methods'])


class Minik:
    """
    Minik is a microframwork that will handle a request from the API gateway and it
    will return a valid http response. The response returned will be determined by
    the view associated with a given route. If the route has a set of path parameters
    the parameters will be given to the view during execution. The view itself will
    have access to the current requests and all it's original data values.

    Very similar to Flask or Chalice, to associate a route to a view use an instance
    of minik to decorate the function:

    @app.route('/events/{event_type}')
    def sample_view(event_type):
        return {'data': ['MD Grand Fondo', 'San Diego Sparta']}

    """

    def __init__(self):
        self._routes = defaultdict(list)

    def route(self, path, **kwargs):
        """
        The decorator function used to associate a given route with a view function.
        """

        def _register_view(view_func):

            methods = kwargs.get('methods', [])
            self._routes[path].append(SimpleRoute(view_func, methods))

            return view_func

        return _register_view

    def __call__(self, event, context):
        """
        The core of the microframework. This method convers the given event to
        a MinikRequest, it looks for the view to execute from the given route, and
        it returns a well defined response. The response will be used by the API
        Gateway to communicate back to the caller.

        :param event: The raw event of the lambda function (straight from API gateway)
        :param context: The aws context included in every lambda function execution
        """

        request = MinikRequest(event, context)
        self.request = request

        try:

            route = self._find_route(request)
            response = self._execute_view(route.view, request)

        except MinikViewError as pe:
            response = JsonResponse({'error_message': str(pe)}, status_code=pe.status_code)
        except Exception as te:
            tracer = ''.join(traceback.format_exc())
            # self.logger.error(tracer)
            response = JsonResponse({'error_message': str(te), 'trace': tracer}, status_code=500)

        return response.to_dict()

    def _execute_view(self, view, request):
        """
        Given a view function, execute the view with the given uri_parameters as
        argumetns and return a JsonResponse.
        """

        if request.uri_params:
            return JsonResponse(view(**request.uri_params))

        return JsonResponse(view())

    def _find_route(self, request):
        """
        Given the paramters of the request, lookup the associated view. The lookup
        process follows a set of steps. If the view is not found an exception is
        raised with the appropriate status code and error message.
        """

        routes = self._routes.get(request.resource)

        if not routes:
            raise MinikViewError(
                'The requested URL was not found on the server.',
                status_code=codes.not_found
            )

        target_route = [route for route in routes if not route.methods or (request.method in route.methods)]

        if not target_route:
            raise MinikViewError(
                'Method is not allowed.',
                status_code=codes.method_not_allowed
            )

        if len(target_route) > 1:
            raise MinikViewError(
                f'Found multiple views for the "{request.method}" method.',
                status_code=codes.not_allowed
            )

        return target_route[0]


class MinikRequest:
    """
    Simple wrapper of the data object received from API Gateway. This object will
    parse a given API gateway event and it will transform it into a more user
    friendly object to operate on. The idea is that a view does not need to be
    concerned with the inner representation of the APIGateway's event as long as
    it has access to the underlaying data values in the event.
    """

    def __init__(self, event, context):

        headers = self._get_with_default(event, 'headers')

        if 'resource' not in event:
            raise ConfigurationError(CONFIG_ERROR_MSG)

        self.resource = event['resource']
        self.query_params = self._get_with_default(event, 'queryStringParameters')
        self.headers = {k.lower(): v for k, v in headers.items()}
        self.uri_params = event['pathParameters']
        self.method = event['requestContext']['httpMethod']
        self._body = event['body']
        # The parsed JSON from the body. This value should
        # only be set if the Content-Type header is application/json,
        # which is the default content type.
        self._json_body = None
        self.aws_context = context

    def _get_with_default(self, event, param_name, default={}):
        return event.get(param_name, {}) or default

    @property
    def json_body(self):
        """
        Lazy loading/parsing of the json payload.
        """
        if self.headers.get('content-type', '').startswith('application/json'):
            if self._json_body is None:
                self._json_body = json.loads(self._body)
            return self._json_body


class JsonResponse:
    """
    A very simple wrapper that defines a valid JsonResponse the APIGateway understands.
    The object encapsulates the headers, status code and body of a response.
    """

    def __init__(self, body, headers=None, status_code=200):
        self.body = body
        self.headers = headers or {}
        self.status_code = status_code

    def to_dict(self, binary_types=None):

        return {
            'headers': self.headers,
            'statusCode': self.status_code,
            'body': json.dumps(self.body)
        }


class MinikError(Exception):
    pass


class MinikViewError(MinikError):
    STATUS_CODE = 500

    def __init__(self, error_message, *args, **kwargs):
        super().__init__(self.__class__.__name__ + ': %s' % error_message)
        self.status_code = kwargs.get('status_code', self.STATUS_CODE)


class BadRequestError(MinikViewError):
    STATUS_CODE = 400


class ConfigurationError(MinikError):
    def __init__(self, error_message, *args, **kwargs):
        super().__init__(self.__class__.__name__ + ': %s' % error_message)
