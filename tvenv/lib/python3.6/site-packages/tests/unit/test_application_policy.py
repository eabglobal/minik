from unittest import TestCase

from serverlessrepo.application_policy import ApplicationPolicy
from serverlessrepo.exceptions import InvalidApplicationPolicyError


class TestApplicationPolicy(TestCase):

    def test_init(self):
        app_policy = ApplicationPolicy(['1', '2'], ['a', 'b'])
        self.assertEqual(app_policy.principals, ['1', '2'])
        self.assertEqual(app_policy.actions, ['a', 'b'])

    def test_valid_principals_actions(self):
        principals = ['123456789011', '*']
        actions = [ApplicationPolicy.DEPLOY, ApplicationPolicy.GET_APPLICATION]
        app_policy = ApplicationPolicy(principals, actions)
        self.assertTrue(app_policy.validate())

    def test_empty_principals(self):
        app_policy = ApplicationPolicy([], [ApplicationPolicy.DEPLOY])
        with self.assertRaises(InvalidApplicationPolicyError) as context:
            app_policy.validate()

        message = str(context.exception)
        expected = 'principals not provided'
        self.assertTrue(expected in message)

    def test_not_12_digits_principals(self):
        app_policy = ApplicationPolicy(['123'], [ApplicationPolicy.DEPLOY])
        with self.assertRaises(InvalidApplicationPolicyError) as context:
            app_policy.validate()

        message = str(context.exception)
        expected = 'principal should be 12-digit AWS account ID or "*"'
        self.assertTrue(expected in message)

    def test_empty_actions(self):
        app_policy = ApplicationPolicy(['123456789012'], [])
        with self.assertRaises(InvalidApplicationPolicyError) as context:
            app_policy.validate()

        message = str(context.exception)
        expected = 'actions not provided'
        self.assertTrue(expected in message)

    def test_not_supported_actions(self):
        app_policy = ApplicationPolicy(['123456789012'], ['RandomActionA', 'RandomActionB'])
        with self.assertRaises(InvalidApplicationPolicyError) as context:
            app_policy.validate()

        message = str(context.exception)
        expected = 'RandomActionA, RandomActionB not supported'
        self.assertTrue(expected in message)

    def test_to_statement(self):
        app_policy = ApplicationPolicy(['1', '2'], ['actionA', 'actionB'])
        expected_statement = {
            'Principals': ['1', '2'],
            'Actions': ['actionA', 'actionB']
        }
        self.assertEqual(app_policy.to_statement(), expected_statement)
