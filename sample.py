import re
PARAM_RE = re.compile("{([a-zA-Z_][a-zA-Z0-9_]*)(:[a-zA-Z_][a-zA-Z0-9_]*)?}")


def compile_path(path):
    path_re = "^"
    idx = 0

    for match in PARAM_RE.finditer(path):
        param_name, convertor_type = match.groups(default="str")

        path_re += path[idx:match.start()]
        path_re += rf"(?P<{param_name}>[^/]+)"

        idx = match.end()

    path_re += path[idx:] + "$"

    return re.compile(path_re)


if __name__ == '__main__':

    re_path = compile_path('/event/{name}/{location}')

    match = re_path.match('/event/pedro_diaz/dc_maryland')

    matched_params = match.groupdict()
    for key, value in matched_params.items():
        matched_params[key] = self.param_convertors[key](value)
