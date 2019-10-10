# -*- coding: utf-8 -*-
"""
    router.py
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

import re
from collections import defaultdict

from minik.exceptions import MinikViewError
from minik.fields import (update_uri_parameters, cache_custom_route_fields)
from minik.status_codes import codes


PARAM_RE = re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)(:[a-zA-Z_][a-zA-Z0-9_]*)?}")


def compile_path(path):
    """
    Utility function to convert a path to a regular expression. A path is defined
    at the route level and it can be defined as having no parameters or multiple
    parameter. Given a definition like '/articles/{month}/{day}', this function will
    return the compiled regex equievanet of it as r'/articles/(?<month>[^/]+)/(?<day>[^/]+)'.

    :param path: The path associated with a route.
    """
    path_re = "^"
    idx = 0

    for match in PARAM_RE.finditer(path):
        param_name, convertor_type = match.groups(default="str")

        path_re += path[idx:match.start()]
        path_re += rf"(?P<{param_name}>[^/]+)"

        idx = match.end()

    path_re += path[idx:] + "$"

    return re.compile(path_re)


class SimpleRoute:
    """
    A class to store function based views for a given path. A route has two core
    components, a path and a function. Once the framework receives a request if
    the path of the request matches the path of the route, this class will know
    how to evaluate the function.
    """
    def __init__(self, route, endpoint, **kwargs):
        self.route = route
        self.endpoint = endpoint
        self.methods = kwargs.get('methods')

        cache_custom_route_fields(self.endpoint)

    def evaluate(self, request, **kwargs):
        update_uri_parameters(self.endpoint, request)
        return self.endpoint(**request.uri_params)


class Router:
    """
    A router holds the collection of routes for the web application. Each route
    has a path and an associated handler. The router knows how to find a route
    for a given request.
    """

    def __init__(self):
        self._routes = defaultdict(list)
        self._compiled_route_paths = list()

    def add_route(self, route_path, endpoint, **kwargs):
        """
        Add a new route to the router. The route path is the identifier associated
        with the given endpoint. The additional set of parameters enhance the definition
        of the route, for instance a set of valid methods=['GET'].

        :param route_path: The identifier of the route to be added. For instance '/books/{year}'.
        :param endpoint: The function or handler associated with the route.
        """
        route_re = compile_path(route_path)
        self._routes[route_path].append(SimpleRoute(route_path, endpoint, **kwargs))

        # Cache the route regular expression to easily lookup the routes for a given
        # request. For instance a request with '/books/2019' => '/books/{year}'. With
        # the generic resource the router can lookup the routes.
        self._compiled_route_paths.append((route_re, route_path))

    def resolve_path(self, path):
        """
        Get the resource and set of path parameters for a given path. If the path
        does not match any of the defined routes, an empty response will be returned.

        :param path: The path associated with a request.
        """

        for path_re, resource in self._compiled_route_paths:
            match = path_re.match(path)
            if match:
                return (resource, dict(match.groupdict()))

        return (None, {})

    def find_route(self, request):
        """
        Given the paramters of the request, lookup the associated view. The lookup
        process follows a this steps:
        1. Lookup get the routes for a given resource
        2. Find the unique route for the method's http request.

        If the view is not found an exception is raised with the appropriate
        status code and error message.

        :param request: An instance of the MinikRequest.
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
