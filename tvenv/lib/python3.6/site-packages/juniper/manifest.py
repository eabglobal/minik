# -*- coding: utf-8 -*-
"""
    manifest.py
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


from pathlib import Path
from itertools import chain


def validate_manifest_definition(manifest_definition):
    """
    Raise errors if problems are found in the manifest file. It checks if
    requirements and include paths exist.
    :param manifest_definition: Dictionary of the manifest
    """
    if missing('requirements', manifest_definition, optional=True):
        raise FileNotFoundError('You have missing requirements files: '
                                f'{missing("requirements", manifest_definition)}')
    if missing('include', manifest_definition):
        raise FileNotFoundError('You have empty include paths: '
                                f'{missing("include", manifest_definition)}')


def missing(key, manifest_definition, optional=False):
    """
    Return all file paths from the key of the manifest that don't exist. Optional
    parameter still does validation when defined.
    :param key: A key in the manifest_definitions functions dictionary
    :param manifest_definition: Dictionary of the manifest
    :param optional: Identifies the key as being required or not. A required key
      will return a missing value array.
    :return: Dictionary of all paths or files that don't exist
    """

    try:
        return [f for f in all_keys(manifest_definition, key)
                if not Path(f).exists()]
    except KeyError as ke:
        return [] if optional else [key]


def all_keys(manifest_definition, key):
    """
    Return all file paths from the key of the manifest.
    :param manifest_definition: Dictionary of the manifest
    :param key: A key in the manifest_definitions functions dictionary
    :return: All paths specified for that key in the manifest file
    """

    result = [function[key] for function in manifest_definition['functions'].values()]
    return result if isinstance(result[0], str) else chain.from_iterable(result)
