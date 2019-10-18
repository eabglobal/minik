from unittest.mock import MagicMock

from minik.exceptions import MinikViewError
from minik.fields import (BaseRouteField, cache_custom_route_fields, CUSTOM_FIELD_BY_TYPE,
                          update_uri_parameters)


def test_cache_custom_route_fields_for_class_based_annotation():
    """
    When the view has a class based annotation, the cache will instantiate the
    class and keep a reference to it.
    """

    class BikesRF(BaseRouteField):
        def validate(self, value):
            return True

    def sample_view(bike_name: BikesRF):
        return {'test': bike_name}

    cache_custom_route_fields(sample_view)

    assert isinstance(CUSTOM_FIELD_BY_TYPE[BikesRF], BikesRF)
    expected_id = id(CUSTOM_FIELD_BY_TYPE[BikesRF])

    # Calling the cache a second time should NOT instantiate a new class.
    cache_custom_route_fields(sample_view)
    assert id(CUSTOM_FIELD_BY_TYPE[BikesRF]) == expected_id


def test_cache_custom_route_fields_for_instance_based_annotation():
    """
    When the view has an instance based annotation, the cache is not updated.
    """

    class BikesPre(BaseRouteField):
        def __init__(self, prefix):
            self._prefix = prefix

        def validate(self, value):
            return True

    def sample_view(bike_name: BikesPre('carbon')):
        return {'test': bike_name}

    orig_len = len(CUSTOM_FIELD_BY_TYPE)
    cache_custom_route_fields(sample_view)

    # Instance based annotations do NOT get cached. These are not cached because
    # the instance is already stored in the function annotation.
    assert BikesPre not in CUSTOM_FIELD_BY_TYPE
    assert orig_len == len(CUSTOM_FIELD_BY_TYPE)


def test_update_uri_parameters_basic_int():

    def sample_view(bike_id: int):
        return {'id': bike_id}

    request = MagicMock(uri_params={'bike_id': '5234'})

    update_uri_parameters(sample_view, request)

    assert request.uri_params['bike_id'] == int('5234')


def test_update_uri_parameters_basic_str():
    """
    With a string based annotated parameter, only valid unicode strings will be
    accepted as valid.
    """

    def sample_view(bike_name: str):
        return {'name': bike_name}

    request = MagicMock(uri_params={'bike_name': '5234'})
    update_uri_parameters(sample_view, request)
    assert request.uri_params['bike_name'] == str('5234')

    request = MagicMock(uri_params={'bike_name': 'scott'})
    update_uri_parameters(sample_view, request)
    assert request.uri_params['bike_name'] == str('scott')

    try:
        request = MagicMock(uri_params={'bike_name': 'sco!!'})
        update_uri_parameters(sample_view, request)
    except MinikViewError as ve:
        assert 'sco!!' in str(ve)


def test_update_uri_parameters_return_hint_is_ignored():
    """
    With a return type hint, only annotated parameter will be
    accepted as valid.
    """

    def sample_view(bike_name: str) -> str:
        return bike_name

    request = MagicMock(uri_params={'bike_name': '5234'})
    update_uri_parameters(sample_view, request)
    assert request.uri_params['bike_name'] == str('5234')

    request = MagicMock(uri_params={'bike_name': 'scott'})
    update_uri_parameters(sample_view, request)
    assert request.uri_params['bike_name'] == str('scott')

    try:
        request = MagicMock(uri_params={'bike_name': 'sco!!'})
        update_uri_parameters(sample_view, request)
    except MinikViewError as ve:
        assert 'sco!!' in str(ve)
