"""Module containing functions to publish or update application."""

import re
import copy

import boto3
from botocore.exceptions import ClientError

from .application_metadata import ApplicationMetadata
from .parser import (
    yaml_dump, parse_template, get_app_metadata,
    parse_application_id, strip_app_metadata
)
from .exceptions import S3PermissionsRequired

CREATE_APPLICATION = 'CREATE_APPLICATION'
UPDATE_APPLICATION = 'UPDATE_APPLICATION'
CREATE_APPLICATION_VERSION = 'CREATE_APPLICATION_VERSION'


def publish_application(template, sar_client=None):
    """
    Create a new application or new application version in SAR.

    :param template: Content of a packaged YAML or JSON SAM template
    :type template: str_or_dict
    :param sar_client: The boto3 client used to access SAR
    :type sar_client: boto3.client
    :return: Dictionary containing application id, actions taken, and updated details
    :rtype: dict
    :raises ValueError
    """
    if not template:
        raise ValueError('Require SAM template to publish the application')

    if not sar_client:
        sar_client = boto3.client('serverlessrepo')

    template_dict = _get_template_dict(template)
    app_metadata = get_app_metadata(template_dict)
    stripped_template_dict = strip_app_metadata(template_dict)
    stripped_template = yaml_dump(stripped_template_dict)
    try:
        request = _create_application_request(app_metadata, stripped_template)
        response = sar_client.create_application(**request)
        application_id = response['ApplicationId']
        actions = [CREATE_APPLICATION]
    except ClientError as e:
        if not _is_conflict_exception(e):
            raise _wrap_s3_exception(e)

        # Update the application if it already exists
        error_message = e.response['Error']['Message']
        application_id = parse_application_id(error_message)
        try:
            request = _update_application_request(app_metadata, application_id)
            sar_client.update_application(**request)
            actions = [UPDATE_APPLICATION]
        except ClientError as e:
            raise _wrap_s3_exception(e)

        # Create application version if semantic version is specified
        if app_metadata.semantic_version:
            try:
                request = _create_application_version_request(app_metadata, application_id, stripped_template)
                sar_client.create_application_version(**request)
                actions.append(CREATE_APPLICATION_VERSION)
            except ClientError as e:
                if not _is_conflict_exception(e):
                    raise _wrap_s3_exception(e)

    return {
        'application_id': application_id,
        'actions': actions,
        'details': _get_publish_details(actions, app_metadata.template_dict)
    }


def update_application_metadata(template, application_id, sar_client=None):
    """
    Update the application metadata.

    :param template: Content of a packaged YAML or JSON SAM template
    :type template: str_or_dict
    :param application_id: The Amazon Resource Name (ARN) of the application
    :type application_id: str
    :param sar_client: The boto3 client used to access SAR
    :type sar_client: boto3.client
    :raises ValueError
    """
    if not template or not application_id:
        raise ValueError('Require SAM template and application ID to update application metadata')

    if not sar_client:
        sar_client = boto3.client('serverlessrepo')

    template_dict = _get_template_dict(template)
    app_metadata = get_app_metadata(template_dict)
    request = _update_application_request(app_metadata, application_id)
    sar_client.update_application(**request)


def _get_template_dict(template):
    """
    Parse string template and or copy dictionary template.

    :param template: Content of a packaged YAML or JSON SAM template
    :type template: str_or_dict
    :return: Template as a dictionary
    :rtype: dict
    :raises ValueError
    """
    if isinstance(template, str):
        return parse_template(template)

    if isinstance(template, dict):
        return copy.deepcopy(template)

    raise ValueError('Input template should be a string or dictionary')


def _create_application_request(app_metadata, template):
    """
    Construct the request body to create application.

    :param app_metadata: Object containing app metadata
    :type app_metadata: ApplicationMetadata
    :param template: A packaged YAML or JSON SAM template
    :type template: str
    :return: SAR CreateApplication request body
    :rtype: dict
    """
    app_metadata.validate(['author', 'description', 'name'])
    request = {
        'Author': app_metadata.author,
        'Description': app_metadata.description,
        'HomePageUrl': app_metadata.home_page_url,
        'Labels': app_metadata.labels,
        'LicenseUrl': app_metadata.license_url,
        'Name': app_metadata.name,
        'ReadmeUrl': app_metadata.readme_url,
        'SemanticVersion': app_metadata.semantic_version,
        'SourceCodeUrl': app_metadata.source_code_url,
        'SpdxLicenseId': app_metadata.spdx_license_id,
        'TemplateBody': template
    }
    # Remove None values
    return {k: v for k, v in request.items() if v}


def _update_application_request(app_metadata, application_id):
    """
    Construct the request body to update application.

    :param app_metadata: Object containing app metadata
    :type app_metadata: ApplicationMetadata
    :param application_id: The Amazon Resource Name (ARN) of the application
    :type application_id: str
    :return: SAR UpdateApplication request body
    :rtype: dict
    """
    request = {
        'ApplicationId': application_id,
        'Author': app_metadata.author,
        'Description': app_metadata.description,
        'HomePageUrl': app_metadata.home_page_url,
        'Labels': app_metadata.labels,
        'ReadmeUrl': app_metadata.readme_url
    }
    return {k: v for k, v in request.items() if v}


def _create_application_version_request(app_metadata, application_id, template):
    """
    Construct the request body to create application version.

    :param app_metadata: Object containing app metadata
    :type app_metadata: ApplicationMetadata
    :param application_id: The Amazon Resource Name (ARN) of the application
    :type application_id: str
    :param template: A packaged YAML or JSON SAM template
    :type template: str
    :return: SAR CreateApplicationVersion request body
    :rtype: dict
    """
    app_metadata.validate(['semantic_version'])
    request = {
        'ApplicationId': application_id,
        'SemanticVersion': app_metadata.semantic_version,
        'SourceCodeUrl': app_metadata.source_code_url,
        'TemplateBody': template
    }
    return {k: v for k, v in request.items() if v}


def _is_conflict_exception(e):
    """
    Check whether the boto3 ClientError is ConflictException.

    :param e: boto3 exception
    :type e: ClientError
    :return: True if e is ConflictException
    """
    error_code = e.response['Error']['Code']
    return error_code == 'ConflictException'


def _wrap_s3_exception(e):
    """
    Wrap S3 access denied exception with a better error message.

    :param e: boto3 exception
    :type e: ClientError
    :return: S3PermissionsRequired if S3 access denied or the original exception
    """
    error_code = e.response['Error']['Code']
    message = e.response['Error']['Message']

    if error_code == 'BadRequestException' and "Failed to copy S3 object. Access denied:" in message:
        match = re.search('bucket=(.+?), key=(.+?)$', message)
        if match:
            return S3PermissionsRequired(bucket=match.group(1), key=match.group(2))

    return e


def _get_publish_details(actions, app_metadata_template):
    """
    Get the changed application details after publishing.

    :param actions: Actions taken during publishing
    :type actions: list of str
    :param app_metadata_template: Original template definitions of app metadata
    :type app_metadata_template: dict
    :return: Updated fields and values of the application
    :rtype: dict
    """
    if actions == [CREATE_APPLICATION]:
        return {k: v for k, v in app_metadata_template.items() if v}

    include_keys = [
        ApplicationMetadata.AUTHOR,
        ApplicationMetadata.DESCRIPTION,
        ApplicationMetadata.HOME_PAGE_URL,
        ApplicationMetadata.LABELS,
        ApplicationMetadata.README_URL
    ]

    if CREATE_APPLICATION_VERSION in actions:
        # SemanticVersion and SourceCodeUrl can only be updated by creating a new version
        additional_keys = [ApplicationMetadata.SEMANTIC_VERSION, ApplicationMetadata.SOURCE_CODE_URL]
        include_keys.extend(additional_keys)
    return {k: v for k, v in app_metadata_template.items() if k in include_keys and v}
