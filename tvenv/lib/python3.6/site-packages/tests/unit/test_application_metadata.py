from unittest import TestCase

from serverlessrepo.application_metadata import ApplicationMetadata
from serverlessrepo.exceptions import InvalidApplicationMetadataError


class TestApplicationMetadata(TestCase):

    def test_init(self):
        app_metadata_dict = {
            'Name': 'name',
            'Description': 'description',
            'Author': 'author',
            'SpdxLicenseId': '123456',
            'LicenseUrl': 's3://bucket/license.txt',
            'ReadmeUrl': 's3://bucket/README.md',
            'Labels': ['label1', 'label2', 'label3'],
            'HomePageUrl': 'https://github.com/my-id/my-repo/',
            'SemanticVersion': '1.0.0',
            'SourceCodeUrl': 's3://bucket/code.zip'
        }
        app_metadata = ApplicationMetadata(app_metadata_dict)
        self.assertEqual(app_metadata.name, app_metadata_dict['Name'])
        self.assertEqual(app_metadata.description, app_metadata_dict['Description'])
        self.assertEqual(app_metadata.author, app_metadata_dict['Author'])
        self.assertEqual(app_metadata.spdx_license_id, app_metadata_dict['SpdxLicenseId'])
        self.assertEqual(app_metadata.license_url, app_metadata_dict['LicenseUrl'])
        self.assertEqual(app_metadata.readme_url, app_metadata_dict['ReadmeUrl'])
        self.assertEqual(app_metadata.labels, app_metadata_dict['Labels'])
        self.assertEqual(app_metadata.home_page_url, app_metadata_dict['HomePageUrl'])
        self.assertEqual(app_metadata.semantic_version, app_metadata_dict['SemanticVersion'])
        self.assertEqual(app_metadata.source_code_url, app_metadata_dict['SourceCodeUrl'])

    def test_invalid_app_metadata(self):
        app_metadata_dict = {'description': 'hello'}
        app_metadata = ApplicationMetadata(app_metadata_dict)
        required_props = ['author', 'name']
        with self.assertRaises(InvalidApplicationMetadataError) as context:
            app_metadata.validate(required_props)

        message = str(context.exception)
        self.assertTrue(', '.join(required_props) in message)

    def test_valid_app_metadata(self):
        app_metadata = ApplicationMetadata({})
        self.assertTrue(app_metadata.validate([]))
