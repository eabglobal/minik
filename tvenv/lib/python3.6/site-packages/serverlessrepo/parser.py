"""Helper to parse JSON/YAML SAM template and dump YAML files."""

import re
import copy
import json
from collections import OrderedDict

import six
import yaml
from yaml.resolver import ScalarNode, SequenceNode

from .application_metadata import ApplicationMetadata
from .exceptions import ApplicationMetadataNotFoundError

METADATA = 'Metadata'
SERVERLESS_REPO_APPLICATION = 'AWS::ServerlessRepo::Application'
APPLICATION_ID_PATTERN = r'arn:[\w\-]+:serverlessrepo:[\w\-]+:[0-9]+:applications\/[\S]+'


def intrinsics_multi_constructor(loader, tag_prefix, node):
    """
    YAML constructor to parse CloudFormation intrinsics.

    :return: a dictionary with key being the instrinsic name
    """
    # Get the actual tag name excluding the first exclamation
    tag = node.tag[1:]

    # Some intrinsic functions doesn't support prefix "Fn::"
    prefix = 'Fn::'
    if tag in ['Ref', 'Condition']:
        prefix = ''

    cfntag = prefix + tag

    if tag == 'GetAtt' and isinstance(node.value, six.string_types):
        # ShortHand notation for !GetAtt accepts Resource.Attribute format
        # while the standard notation is to use an array
        # [Resource, Attribute]. Convert shorthand to standard format
        value = node.value.split('.', 1)

    elif isinstance(node, ScalarNode):
        # Value of this node is scalar
        value = loader.construct_scalar(node)

    elif isinstance(node, SequenceNode):
        # Value of this node is an array (Ex: [1,2])
        value = loader.construct_sequence(node)

    else:
        # Value of this node is an mapping (ex: {foo: bar})
        value = loader.construct_mapping(node)

    return {cfntag: value}


def _dict_representer(dumper, data):
    return dumper.represent_dict(data.items())


def yaml_dump(dict_to_dump):
    """
    Dump the dictionary as a YAML document.

    :param dict_to_dump: Data to be serialized as YAML
    :type dict_to_dump: dict
    :return: YAML document
    :rtype: str
    """
    yaml.SafeDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.safe_dump(dict_to_dump, default_flow_style=False)


def _dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))


def parse_template(template_str):
    """
    Parse the SAM template.

    :param template_str: A packaged YAML or json CloudFormation template
    :type template_str: str
    :return: Dictionary with keys defined in the template
    :rtype: dict
    """
    try:
        # PyYAML doesn't support json as well as it should, so if the input
        # is actually just json it is better to parse it with the standard
        # json parser.
        return json.loads(template_str, object_pairs_hook=OrderedDict)
    except ValueError:
        yaml.SafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _dict_constructor)
        yaml.SafeLoader.add_multi_constructor('!', intrinsics_multi_constructor)
        return yaml.safe_load(template_str)


def get_app_metadata(template_dict):
    """
    Get the application metadata from a SAM template.

    :param template_dict: SAM template as a dictionary
    :type template_dict: dict
    :return: Application metadata as defined in the template
    :rtype: ApplicationMetadata
    :raises ApplicationMetadataNotFoundError
    """
    if SERVERLESS_REPO_APPLICATION in template_dict.get(METADATA, {}):
        app_metadata_dict = template_dict.get(METADATA).get(SERVERLESS_REPO_APPLICATION)
        return ApplicationMetadata(app_metadata_dict)

    raise ApplicationMetadataNotFoundError(
        error_message='missing {} section in template Metadata'.format(SERVERLESS_REPO_APPLICATION))


def parse_application_id(text):
    """
    Extract the application id from input text.

    :param text: text to parse
    :type text: str
    :return: application id if found in the input
    :rtype: str
    """
    result = re.search(APPLICATION_ID_PATTERN, text)
    return result.group(0) if result else None


def strip_app_metadata(template_dict):
    """
    Strip the "AWS::ServerlessRepo::Application" metadata section from template.

    :param template_dict: SAM template as a dictionary
    :type template_dict: dict
    :return: stripped template content
    :rtype: str
    """
    if SERVERLESS_REPO_APPLICATION not in template_dict.get(METADATA, {}):
        return template_dict

    template_dict_copy = copy.deepcopy(template_dict)

    # strip the whole metadata section if SERVERLESS_REPO_APPLICATION is the only key in it
    if not [k for k in template_dict_copy.get(METADATA) if k != SERVERLESS_REPO_APPLICATION]:
        template_dict_copy.pop(METADATA, None)
    else:
        template_dict_copy.get(METADATA).pop(SERVERLESS_REPO_APPLICATION, None)

    return template_dict_copy
