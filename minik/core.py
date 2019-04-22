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

from collections import namedtuple, defaultdict
from minik.fields import (update_uri_parameters, cache_custom_route_fields)

from minik.exceptions import MinikViewError
from minik.models import Response
from minik.builders import APIGatewayRequestBuilder
from minik.middleware import ServerErrorMiddleware, ExceptionMiddleware, ContentTypeMiddleware
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

    def __init__(self, **kwargs):
        self._debug = kwargs.get('debug', False)

        self._request_builder = kwargs.get('request_builder', APIGatewayRequestBuilder())
        self._error_middleware = kwargs.get('server_error_middleware', ServerErrorMiddleware())
        self._exception_middleware = kwargs.get('exception_middleware', ExceptionMiddleware)

        self._routes = defaultdict(list)
        self._middleware = [
            ContentTypeMiddleware()
        ]

    @property
    def in_debug(self):
        return self._debug

    def add_middleware(self, middleware_instance):
        self._middleware.append(middleware_instance)

    def get(self, path, **kwargs):
        return self.route(path, methods=['GET'], **kwargs)

    def post(self, path, **kwargs):
        return self.route(path, methods=['POST'], **kwargs)

    def put(self, path, **kwargs):
        return self.route(path, methods=['PUT'], **kwargs)

    def delete(self, path, **kwargs):
        return self.route(path, methods=['DELETE'], **kwargs)

    def route(self, path, **kwargs):
        """
        The decorator function used to associate a given route with a view function.

        :param path: The endpoint associated with a given view.
        """

        def _register_view(view_func):

            methods = kwargs.get('methods', [])
            new_route = SimpleRoute(view_func, methods)
            self._routes[path].append(new_route)
            cache_custom_route_fields(new_route)

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

        request = self._request_builder.build(event, context)
        self.request = request
        self.response = Response(
            status_code=codes.ok,
            headers={'Content-Type': 'application/json'}
        )

        try:

            route = self._find_route(request)
            update_uri_parameters(route, request)
            self._execute_view(route.view)

        except MinikViewError as mve:
            self._error_middleware(self, mve)
        except Exception as e:
            self._exception_middleware(self, e)

        for middleware in self._middleware:
            middleware(self)

        return self.response.to_dict()

    def _execute_view(self, view):
        """
        Given a view function, execute the view with the given uri_parameters as
        argumetns and return a.
        """

        self.response.body = view(**self.request.uri_params) if self.request.uri_params else view()

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


class BadRequestError(MinikViewError):
    STATUS_CODE = codes.bad_request
