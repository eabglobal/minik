import re
from minik.exceptions import MinikViewError
from minik.status_codes import codes


class RePath:
    """
    Regex based router field. This base class will use the pattern field of a
    subclass as a way to validate a given value. If the value matches the pattern
    nothing happens. If it does not, a ValueError is raised.
    """
    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def __call__(self, value):
        """
        Validate that the given value matches the pattern. If value does not match
        raise a ValueError.

        :param value: The value to match against the pattern.
        """
        if self._pattern.match(value):
            return value

        raise ValueError(f"invalid literal for {self.__class__.__name__}(): '{value}'")


CUSTOM_FIELD_BY_TYPE = {
    str: RePath(r'^(\w+)$')
}


def update_uri_parameters(route, request):

    values_by_name = request.uri_params

    try:

        for field_name, field_type in route.view.__annotations__.items():
            new_field_type = CUSTOM_FIELD_BY_TYPE.get(field_type, field_type)
            values_by_name[field_name] = new_field_type(values_by_name[field_name])

    except ValueError as ve:
        raise MinikViewError(str(ve), status_code=codes.not_found)
