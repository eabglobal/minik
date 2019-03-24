import re
from minik.exceptions import MinikViewError
from minik.status_codes import codes


class NopValidator:
    def validate(self, route, request):
        pass


class ReValidator:

    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def validate(self, route, request):

        matched = self._pattern.match(request.path)
        if not matched:
            raise MinikViewError(
                'Path validation error.',
                status_code=codes.not_found
            )
