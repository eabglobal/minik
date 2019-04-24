from minik.status_codes import codes


class MinikError(Exception):
    pass


class MinikViewError(MinikError):
    STATUS_CODE = codes.server_error

    def __init__(self, error_message, *args, **kwargs):
        super().__init__(f'{self.__class__.__name__}: {error_message}')
        self.status_code = kwargs.get('status_code', self.STATUS_CODE)


class ConfigurationError(MinikError):
    def __init__(self, error_message, *args, **kwargs):
        super().__init__(self.__class__.__name__ + ': %s' % error_message)
