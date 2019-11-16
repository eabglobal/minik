import re
import inspect
from abc import ABC, abstractmethod

from minik.exceptions import MinikViewError
from minik.status_codes import codes


class BaseRouteField(ABC):

    def __call__(self, value):
        """
        The method called to perform a given validation. If the validation is
        successful, the route field is returned unchanged. If the validation fails,
        a ValueError is raised.

        :param value: The value to match against the pattern.
        """
        if self.validate(value):
            return value

        raise ValueError(f"invalid literal for {self.__class__.__name__}(): '{value}'")

    @abstractmethod
    def validate(self, value):
        """
        Business logic that must be implemented by a consumer to determine if
        the given route value is valid or not. True=valid, False=invalid.

        :param vaule: The actual value of a route field.
        """
        pass


class ReStr(BaseRouteField):
    """
    Regex based router field. This class will use the pattern value of an
    instance to validate a given value. If the value matches the pattern,
    nothing happens. If it does not, a ValueError is raised.
    """
    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def validate(self, value):
        """
        Validate that the given value matches the regex pattern.

        :param value: The value to match against the pattern.
        """
        return self._pattern.match(value)


CUSTOM_FIELD_BY_TYPE = {
    str: ReStr(r'^([\w-]+)$')
}


def update_uri_parameters(view_fn, request):
    """
    Based on the function annotations of the route's view, validate a given route
    parameter and update the value of the requests' uri. For example, a route is
    defined as follows:

    def my_view(product_id: int):
        return {'id': product_id}

    This function will validate that the given value in the url is an integer and
    it will update the string value of the request.uri_parameters to be the int
    representation of the value.

    :param view_fn: The function that will be executed for a given endpoint.
    :param request: The instance of the minik request.
    """

    values_by_name = request.uri_params

    try:

        for field_name, field_type in view_fn.__annotations__.items():
            if field_name == 'return':
                #  Ignore 'return' field_name if type hint exists for view_fn
                continue
            new_field_type = CUSTOM_FIELD_BY_TYPE.get(field_type, field_type)
            values_by_name[field_name] = new_field_type(values_by_name[field_name])

    except ValueError as ve:
        raise MinikViewError(str(ve), status_code=codes.not_found)


def cache_custom_route_fields(view):
    """
    For class based view annotations, create an instance of the class and store
    the instance in a cache. This instance will be used by a consumer to validate
    a route paramter.

    If the annotated field is an instantiated value, it will NOT be added to the
    cache.

    :param view: Any function that contains a set of parameter annotations.
    """

    for field_name, field_type in view.__annotations__.items():
        if field_type in CUSTOM_FIELD_BY_TYPE:
            continue

        if issubclass(field_type, BaseRouteField) and inspect.isclass(BaseRouteField):
            CUSTOM_FIELD_BY_TYPE[field_type] = field_type()
