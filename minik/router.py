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

    def __init__(self, route, endpoint, **kwargs):
        self.route = route
        self.endpoint = endpoint
        self.methods = kwargs.get('methods')

        cache_custom_route_fields(self.endpoint)

    def evaluate(self, request, **kwargs):
        update_uri_parameters(self.endpoint, request)
        return self.endpoint(**request.uri_params)


class Router:

    def __init__(self):
        self._routes = defaultdict(list)
        self._compiled_route_paths = list()

    def add_route(self, route_path, endpoint, **kwargs):

        route_re = compile_path(route_path)
        self._routes[route_path].append(SimpleRoute(route_path, endpoint, **kwargs))
        self._compiled_route_paths.append((route_re, route_path))

    def resolve_path(self, path):

        for path_re, resource in self._compiled_route_paths:
            match = path_re.match(path)
            if match:
                return (resource, dict(match.groupdict()))

        return (None, {})

    def find_route(self, request):
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
