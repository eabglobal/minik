"""Module containing class to store SAR application permissions."""

import re

from .exceptions import InvalidApplicationPolicyError


class ApplicationPolicy(object):
    """Class representing SAR application policy."""

    # Supported actions for setting SAR application permissions
    GET_APPLICATION = 'GetApplication'
    LIST_APPLICATION_DEPENDENCIES = 'ListApplicationDependencies'
    CREATE_CLOUD_FORMATION_CHANGE_SET = 'CreateCloudFormationChangeSet'
    CREATE_CLOUD_FORMATION_TEMPLATE = 'CreateCloudFormationTemplate'
    LIST_APPLICATION_VERSIONS = 'ListApplicationVersions'
    SEARCH_APPLICATIONS = 'SearchApplications'
    DEPLOY = 'Deploy'

    SUPPORTED_ACTIONS = [
        GET_APPLICATION,
        LIST_APPLICATION_DEPENDENCIES,
        CREATE_CLOUD_FORMATION_CHANGE_SET,
        CREATE_CLOUD_FORMATION_TEMPLATE,
        LIST_APPLICATION_VERSIONS,
        SEARCH_APPLICATIONS,
        DEPLOY
    ]

    _PRINCIPAL_PATTERN = re.compile(r'^([0-9]{12}|\*)$')

    def __init__(self, principals, actions):
        """
        Initialize the object given the principals and actions.

        :param principals: List of AWS account IDs, or *
        :type principals: list of str
        :param actions: List of actions supported by SAR
        :type actions: list of str
        """
        self.principals = principals
        self.actions = actions

    def validate(self):
        """
        Check if the formats of principals and actions are valid.

        :return: True, if the policy is valid
        :raises: InvalidApplicationPolicyError
        """
        if not self.principals:
            raise InvalidApplicationPolicyError(error_message='principals not provided')

        if not self.actions:
            raise InvalidApplicationPolicyError(error_message='actions not provided')

        if any(not self._PRINCIPAL_PATTERN.match(p) for p in self.principals):
            raise InvalidApplicationPolicyError(
                error_message='principal should be 12-digit AWS account ID or "*"')

        unsupported_actions = sorted(set(self.actions) - set(self.SUPPORTED_ACTIONS))
        if unsupported_actions:
            raise InvalidApplicationPolicyError(
                error_message='{} not supported'.format(', '.join(unsupported_actions)))

        return True

    def to_statement(self):
        """
        Convert to a policy statement dictionary.

        :return: Dictionary containing Actions and Principals
        :rtype: dict
        """
        return {
            'Principals': self.principals,
            'Actions': self.actions
        }
