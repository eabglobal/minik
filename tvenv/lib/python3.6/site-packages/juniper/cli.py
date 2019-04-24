import os
import click
import click_log
import pathlib
import shutil
import logging

from juniper.io import reader
from juniper.constants import DEFAULT_OUT_DIR
from juniper.actions import build_artifacts
from juniper.manifest import validate_manifest_definition


logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.group()
def main():
    """
    Juniper is a packaging tool with a with a single purpose in mind:
    stream and standardize the creation of a zip artifact for a set of
    AWS lambda functions.
    """
    pass


# @main.command(help="""""")
# @click_log.simple_verbosity_option(logger)
# def package():
#     # TODO: Implement me
#     pass


@main.command(help="""Packages a set of lambda functions defined in a given manifest file.
                      The manifest must defined these parameters:
                      1 - The name of each function to package
                      2 - A clear path to the dependencies of each lambda function
                      3 - The actual codebase to include in each zip file
                    """)
@click.option('--manifest', '-m', default='manifest.yml', help='The configuration file to use.')
@click.option('--debug', '-d', is_flag=True, help='Run the build in debug mode.')
@click.option('--skip-clean', '-s', is_flag=True, help='Does recreate the output directory.')
@click_log.simple_verbosity_option(logger)
def build(manifest, debug, skip_clean):

    if debug:
        logger.setLevel(logging.DEBUG)

    try:
        if manifest == 'manifest.yml' and not pathlib.Path('manifest.yml').is_file():
            manifest = 'manifest.yaml'
        manifest_definition = reader(manifest)
        validate_manifest_definition(manifest_definition)
    except FileNotFoundError as fnf:
        logger.error(str(fnf))
    else:
        old_output = manifest_definition.get('package', {}).get('output')
        if old_output:
            logger.error("The package section in the manifest is deprecated. Please use the global section")
            return

        # Set the value of output_dir in the manifest either from the custom value
        # provided or from the default.
        output_dir = manifest_definition.get('global', {}).get('output', DEFAULT_OUT_DIR)
        manifest_definition['output_dir'] = output_dir

        # Get the local env ready before building the artifacts.
        _clean(logger, skip_clean, manifest_definition)
        build_artifacts(logger, manifest_definition)


def _clean(logger, skip, manifest):
    """
    Clean the working environment before building a new set of artifacts. The clean
    operation will completely rm -f the output directory and then it will create
    a brand new directory.

    :param logger: The logger instance used by juniper.
    :param skip: A flag that indicates weather or not the clean process should
                 be executed
    :param manifest: The manifest that contains all the build parameters.
    """

    output_dir = manifest['output_dir']

    if skip:
        logger.debug('Skipping the cleaning process.')

        # The very first time the build command is executed, if the output
        # directory does not exist, we need to create it. This does not override
        # an existing directory.
        os.makedirs(output_dir, exist_ok=True)
        return

    logger.debug(f'Executing: rm -rf {output_dir} && mkdir {output_dir}')
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)


if __name__ == '__main__':
    main()
