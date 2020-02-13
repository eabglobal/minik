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

from contextlib import contextmanager

from minik.exceptions import MinikViewError
from minik.models import Response
from minik.builders import build_request
from minik.router import Router
from minik.middleware import (ServerErrorMiddleware, ExceptionMiddleware, ContentTypeMiddleware)
from minik.status_codes import codes


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

        self._router = Router()
        self._error_middleware = kwargs.get('server_error_middleware', ServerErrorMiddleware())
        self._exception_middleware = kwargs.get('exception_middleware', ExceptionMiddleware())

        self._middleware = [ContentTypeMiddleware()]

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

    def patch(self, path, **kwargs):
        return self.route(path, methods=['PATCH'], **kwargs)

    def delete(self, path, **kwargs):
        return self.route(path, methods=['DELETE'], **kwargs)

    def route(self, path, **kwargs):
        """
        The decorator function used to associate a given route path to a handler.

        @route('/events/{event_id}')
        def get_event(event_id: str):
            pass

        :param path: The endpoint associated with a given view.
        """

        def _register_view(view_func):
            self._router.add_route(path, view_func, **kwargs)
            return view_func

        return _register_view

    def __call__(self, event, context):
        """
        The entrypoint of a lambda function. When building a web app with minik,
        the app instance must be the handler of the lambda function. Minik will
        be responsible for consuming the raw event and context objects sent by the
        consumer service.

        The workflow of the framework is the following:
        1) Normalize the given event
        2) Find the route associated with the request
        3) Execute the handler associated with the route
        4) Run any additional middleware classes

        :param event: The raw event of the lambda function (straight from API Gateway/ALB)
        :param context: The aws context included in every lambda function execution
        """

        # Normalize the raw event by type and build a MinikRequest.
        self.request = build_request(event, context, self._router)
        self.response = Response(
            status_code=codes.ok,
            headers={'Content-Type': 'application/json'}
        )

        with error_handling(self):
            route = self._router.find_route(self.request)
            self.response.body = route.evaluate(self.request)

        # After executing the view run all the middlewares in sequence. If a middleware
        # fails, handle the exception and move on. This code needs to run after the
        # execution of the views in its own contenxt given that we do want to run this
        # even if the view itself raised an exception.
        with error_handling(self):
            for middleware in self._middleware:
                middleware(self)

        return self.response.to_dict()


@contextmanager
def error_handling(minik_app):
    """
    Context manager used to handle both server side errors and unhandled exceptions.
    Both cases will be delegated to the appropriate middleware of the minik app
    instance.

    :param minik_app: The instance of the minik app framework.
    """

    try:
        yield
    except MinikViewError as mve:
        minik_app._error_middleware(minik_app, mve)
    except Exception as e:
        minik_app._exception_middleware(minik_app, e)


class BadRequestError(MinikViewError):
    STATUS_CODE = codes.bad_request
