import json
import pytest

from unittest.mock import MagicMock
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
