"""Module containing methods to manage application permissions."""

import boto3

from .application_policy import ApplicationPolicy


def make_application_public(application_id, sar_client=None):
    """
    Set the application to be public.

    :param application_id: The Amazon Resource Name (ARN) of the application
    :type application_id: str
    :param sar_client: The boto3 client used to access SAR
    :type sar_client: boto3.client
    :raises ValueError
    """
    if not application_id:
        raise ValueError('Require application id to make the app public')

    if not sar_client:
        sar_client = boto3.client('serverlessrepo')

    application_policy = ApplicationPolicy(['*'], [ApplicationPolicy.DEPLOY])
    application_policy.validate()
    sar_client.put_application_policy(
        ApplicationId=application_id,
        Statements=[application_policy.to_statement()]
    )


def make_application_private(application_id, sar_client=None):
    """
    Set the application to be private.

    :param application_id: The Amazon Resource Name (ARN) of the application
    :type application_id: str
    :param sar_client: The boto3 client used to access SAR
    :type sar_client: boto3.client
    :raises ValueError
    """
    if not application_id:
        raise ValueError('Require application id to make the app private')

    if not sar_client:
        sar_client = boto3.client('serverlessrepo')

    sar_client.put_application_policy(
        ApplicationId=application_id,
        Statements=[]
    )


def share_application_with_accounts(application_id, account_ids, sar_client=None):
    """
    Share the application privately with given AWS account IDs.

    :param application_id: The Amazon Resource Name (ARN) of the application
    :type application_id: str
    :param account_ids: List of AWS account IDs, or *
    :type account_ids: list of str
    :param sar_client: The boto3 client used to access SAR
    :type sar_client: boto3.client
    :raises ValueError
    """
    if not application_id or not account_ids:
        raise ValueError('Require application id and list of AWS account IDs to share the app')

    if not sar_client:
        sar_client = boto3.client('serverlessrepo')

    application_policy = ApplicationPolicy(account_ids, [ApplicationPolicy.DEPLOY])
    application_policy.validate()
    sar_client.put_application_policy(
        ApplicationId=application_id,
        Statements=[application_policy.to_statement()]
    )
