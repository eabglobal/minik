from contextlib import contextmanager


@contextmanager
def safe_execute(*args, **kwds):

    try:

        yield

    except MinikViewError as mve:
        self._error_middleware(self, mve)
    except Exception as e:
        self._exception_middleware(self, e)
