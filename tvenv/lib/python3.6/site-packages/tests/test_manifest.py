# -*- coding: utf-8 -*-
"""
    test_manifest.py
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

import pytest

from juniper.manifest import validate_manifest_definition


def test_source_in_manifest_does_not_exist_notifies_dev():

    manifest_definition = {'package': {'output': './build'},
                           'functions': {'sample': {'requirements': './requirements/dev.txt',
                                                    'include': ['./']},
                                         'another': {'requirements': './requirements/dev.txt',
                                                     'include': ['./idontexist']}}}

    with pytest.raises(FileNotFoundError) as e:
        validate_manifest_definition(manifest_definition)

    assert str(e.value) == "You have empty include paths: ['./idontexist']"


def test_requirements_in_manifest_does_not_exist_notifies_dev():
    """
    If the requirements field has a value, the files it points to, must be valid.
    """

    manifest_definition = {'package': {'output': './build'},
                           'functions': {'sample': {'requirements': './idontexist.txt',
                                                    'include': ['./']},
                                         'another': {'requirements': './requirements/dev.txt',
                                                     'include': ['./']}}}

    with pytest.raises(FileNotFoundError) as e:
        validate_manifest_definition(manifest_definition)

    assert str(e.value) == "You have missing requirements files: ['./idontexist.txt']"


def test_requirements_not_a_required_field():
    """
    A requirements file is NOT required! If it is ommited from the manifest file,
    do nothing.
    """

    manifest_definition = {'package': {'output': './build'},
                           'functions': {'sample': {'include': ['./']},
                                         'another': {'requirements': './requirements/dev.txt',
                                                     'include': ['./']}}}

    validate_manifest_definition(manifest_definition)
    assert True


def test_include_section_is_required():
    """
    Test with missing requirements section (valid) and a misspell on the includes.
    """

    manifest_definition = {'package': {'output': './build'},
                           'functions': {'sample': {'includes': ['./']},
                                         'another': {'requirements': './requirements/dev.txt',
                                                     'include': ['./']}}}
    with pytest.raises(FileNotFoundError) as e:
        validate_manifest_definition(manifest_definition)

    assert len(str(e))
