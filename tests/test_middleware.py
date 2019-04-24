import json
import pytest

from unittest.mock import MagicMock
from minik.core import Minik
from minik.models import Response
from minik.middleware import (ContentTypeMiddleware, ServerErrorMiddleware)


@pytest.mark.parametrize("sample_header", [
    'Content-Type', 'content-type', 'content-Type'
])
def test_content_type_application_json(sample_header):

    response = Response(
        headers={sample_header: 'application/json'},
        body={'findme': True}
    )
    mock_app = MagicMock(response=response)

    ContentTypeMiddleware()(mock_app)

    assert response.body == json.dumps({'findme': True})


def test_server_error_middleware():

    error = MagicMock(status_code=432)
    mock_app = MagicMock(response=Response())

    ServerErrorMiddleware()(mock_app, error)

    assert mock_app.response.status_code == error.status_code
    assert mock_app.response.body == {'error_message': str(error)}


class CustomMiddleware:
    expected_header_value = 'JuniperRidge'

    def __call__(self, app, *args, **kwargs):
        app.response.headers['x-findme'] = self.expected_header_value


def test_custom_middleware_updates_response(create_router_event):
    """
    Make sure that a custom middleware is executed as part of the workflow of
    handling a request.
    """

    app = Minik()
    app.add_middleware(CustomMiddleware())

    @app.get('/event')
    def get_event():
        return {'data': 'some event'}

    event = create_router_event('/event', method='GET')

    response = app(event, MagicMock())

    assert response['headers']['x-findme'] == CustomMiddleware.expected_header_value


def test_custom_middleware_updates_response_view_fails(create_router_event):
    """
    Make sure that a custom middleware is executed as part of the workflow of
    handling a request.
    """

    app = Minik()
    app.add_middleware(CustomMiddleware())

    @app.get('/event')
    def get_event():
        raise Exception('Something went downhill :(')

    event = create_router_event('/event', method='GET')

    response = app(event, MagicMock())

    assert response['headers']['x-findme'] == CustomMiddleware.expected_header_value
