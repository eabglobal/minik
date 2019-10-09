from unittest.mock import MagicMock
from minik.builders import ALBRequestBuilder


class TestALBRequestBuilder:

    def test_build_with_querystrings(self, create_alb_event):

        mock_router = MagicMock()
        mock_router.resolve_path.return_value = ('resource', {})

        alb_event = create_alb_event(path='/findme', queryParameters={'findme': 'now'})

        result = ALBRequestBuilder().build(alb_event, 'context', mock_router)

        assert result.query_params['findme'] == 'now'

    def test_build_urldecodes_querystrings(self, create_alb_event):

        mock_router = MagicMock()
        mock_router.resolve_path.return_value = ('resource', {})

        alb_event = create_alb_event(path='/findme', queryParameters={'foo%5Ba%5D': 'foo%5B'})

        result = ALBRequestBuilder().build(alb_event, 'context', mock_router)

        assert result.query_params['foo[a]'] == 'foo['
