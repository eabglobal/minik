# -*- coding: utf-8 -*-
"""
    test_manifest_params.py
    :copyright: © 2019 by the EAB Tech team.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import yaml

from juniper import actions, constants
from unittest.mock import MagicMock
from juniper.io import reader


logger = MagicMock()


def test_build_compose_sections_custom_docker_images():
    """
    Given a sample manifest file with a set of docker-image overrides,
    validate that when building the docker compose template, the result
    produces a valid template.
    """

    docker_ctx = reader('./tests/manifests/custom-docker-images.yml')
    result = actions._get_compose_template(docker_ctx)

    expected = read_file('./tests/expectations/custom-docker-images.yml')
    assert yaml.safe_load(result) == yaml.safe_load(expected)


def test_get_docker_image_default():
    """
    No customizations at all. Make sure the default docker image is used.
    """

    sls_function = {}
    manifest = {'global': {}}

    image = actions._get_docker_image(manifest, sls_function)
    assert image == constants.DEFAULT_DOCKER_IMAGE


def test_get_docker_image_global_override():
    """
    Override at the global level.
    """

    sls_function = {}
    manifest = {'global': {'image': 'python:3.6-alpine'}}

    image = actions._get_docker_image(manifest, sls_function)
    assert image == 'python:3.6-alpine'


def test_get_docker_image_funcion_level_override():

    manifest = {'global': {}}
    sls_function = {'image': 'python:3.8-alpine'}

    image = actions._get_docker_image(manifest, sls_function)
    assert image == 'python:3.8-alpine'


def test_get_docker_image_function_precedence():

    sls_function = {'image': 'python:3.8-alpine'}
    manifest = {'global': {'image': 'python:ignore_me'}}

    image = actions._get_docker_image(manifest, sls_function)
    assert image == 'python:3.8-alpine'


def read_file(file_name):
    with open(file_name, 'r') as f:
        return f.read()
