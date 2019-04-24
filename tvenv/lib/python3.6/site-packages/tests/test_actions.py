# -*- coding: utf-8 -*-
"""
    test_actions.py
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

from juniper import actions
from unittest.mock import MagicMock
from juniper.io import reader, get_artifact_path


logger = MagicMock()


def test_build_compose_writes_compose_definition_to_tmp_file(mocker):
    """
    The docker-compose file created, is written to a tmp file. Make sure that
    the file is writen and validate that the contents of the file match the
    expected result.
    """

    tmp_filename = '/var/folders/xw/yk2rrhks1w72y0zr_7t7b851qlt8b3/T/tmp52bd77s3'
    mock_writer = mocker.patch('juniper.actions.write_tmp_file', return_value=tmp_filename)

    processor_ctx = reader('./tests/manifests/processor-test.yml')
    actual_filename = actions.build_compose(logger, processor_ctx)

    expected = read_file('./tests/expectations/processor-compose.yml')

    assert tmp_filename == actual_filename
    assert yaml.safe_load(mock_writer.call_args[0][0]) == yaml.safe_load(expected)


def test_build_artifacts_invokes_docker_commands(mocker):
    """
    Validate that the docker-compose commands are executed with the valid paramters.
    Since the docker-compose file was dynamically generated, we must pass the full
    path of that file to docker-compose command. Also, set the context of the execution
    to the current path.
    """

    tmp_filename = '/var/folders/xw/yk2rrhks1w72y0zr_7t7b851qlt8b3/T/tmp52bd77s3'
    mock_builder = mocker.patch('juniper.actions.build_compose', return_value=tmp_filename)

    # Mocking the dependencies of this action. These three high level packages are
    # needed to invoke docker-compose in the right context!
    mocker.patch('juniper.actions.os')
    mocker.patch('juniper.actions.shutil')
    mock_subprocess_run = mocker.patch('juniper.actions.subprocess.run')

    compose_cmd_calls = [
        mocker.call(["docker-compose", "-f", tmp_filename, '--project-directory', '.', 'down']),
        mocker.call(["docker-compose", "-f", tmp_filename, '--project-directory', '.', 'up'])
    ]

    processor_ctx = reader('./tests/manifests/processor-test.yml')
    actions.build_artifacts(logger, processor_ctx)

    mock_subprocess_run.assert_has_calls(compose_cmd_calls)
    mock_builder.assert_called_once()


def test_build_artifacts_copies_scriopts(mocker):
    """
    Since the docker-compose command will be executed from within the context
    of where the lambda functions live. We need to make sure that the `package.sh`
    lives in the right context.

    Validate that a bin folder is temporarily created in the folder of the caller.
    This folder will be removed after the .zip artifacts are generated.
    """

    tmp_filename = '/var/folders/xw/yk2rrhks1w72y0zr_7t7b851qlt8b3/T/tmp52bd77s3'
    mock_builder = mocker.patch('juniper.actions.build_compose', return_value=tmp_filename)

    # Mocking the dependencies of this action. These three high level packages are
    # needed to invoke docker-compose in the right context!
    mock_os = mocker.patch('juniper.actions.os')
    mock_shutil = mocker.patch('juniper.actions.shutil')
    mocker.patch('juniper.actions.subprocess.run')

    processor_ctx = reader('./tests/manifests/processor-test.yml')
    actions.build_artifacts(logger, processor_ctx)

    # Validate that this three step process is correctly executed.
    mock_os.makedirs.assert_called_with('./.juni/bin', exist_ok=True)
    mock_shutil.copy.assert_called_with(get_artifact_path('package.sh'), './.juni/bin/')
    mock_shutil.rmtree.assert_called_with('./.juni', ignore_errors=True)
    mock_builder.assert_called_once()


def test_build_compose_section_custom_output():
    """
    Validate that given a custom output directory, the volume mapping incldues
    the custom value instead of the default dist.
    """

    custom_output_dir = './build_not_dist'
    manifest = {
        'output_dir': custom_output_dir,
        'functions': {'test_func': {}}
    }

    result = actions._get_compose_template(manifest)
    yaml_result = yaml.safe_load(result)

    assert len([
        volume.strip()
        for volume in yaml_result['services']['test_func-lambda']['volumes']
        if custom_output_dir in volume
    ])


def test_get_volumes_fixes_trailing_slash():
    """
    If the include entry contains a trailing slash, the mapped version should NOT have it.
    """

    sls_function = {'include': ['./src/function1/']}
    manifest = {'functions': {'router': sls_function}}

    volumes = actions._get_volumes(manifest, sls_function)

    expected_mapping = './src/function1:/var/task/common/function1'
    assert expected_mapping in volumes


def test_get_volumes_with_mixed_entries():

    sls_function = {
        'include': [
            './src/common/',
            './src/benchmark',
            './src/trail',
        ]
    }
    manifest = {'functions': {'router': sls_function}}

    volumes = actions._get_volumes(manifest, sls_function)

    tmpl = './src/{name}:/var/task/common/{name}'
    assert tmpl.format(name='common') in volumes
    assert tmpl.format(name='benchmark') in volumes
    assert tmpl.format(name='trail') in volumes


def test_get_volumes_current_path():

    sls_function = {
        'include': ['./']
    }
    manifest = {'functions': {'router': sls_function}}

    volumes = actions._get_volumes(manifest, sls_function)

    assert './:/var/task/common/' in volumes


def test_get_volumes_with_files():

    sls_function = {
        'include': ['./src/lambda_function.py']
    }
    manifest = {'functions': {'router': sls_function}}

    volumes = actions._get_volumes(manifest, sls_function)

    assert './src/lambda_function.py:/var/task/common/lambda_function.py' in volumes


def read_file(file_name):
    with open(file_name, 'r') as f:
        return f.read()
