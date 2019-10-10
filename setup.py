import io
import re
from collections import OrderedDict
from setuptools import setup, find_packages


with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = ''.join([line for line in f.readlines() if '.. image::' not in line])

# Make sure that the version of the package always matches the version of the
# tool. The version of the __init__.py is updated with the make release command.
with io.open('minik/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='minik',
    version=version,
    description='Web framework for the serverless domain',
    long_description=readme,
    long_description_content_type='text/x-rst',
    url='https://github.com/eabglobal/minik',
    project_urls=OrderedDict((
        ('Code', 'https://github.com/eabglobal/minik'),
        ('Issue tracker', 'https://github.com/eabglobal/minik/issues'),
    )),
    license='Apache Software License',
    author='EAB tech',
    author_email='opensource@eab.com',
    packages=find_packages(),
    include_package_data=True,
    test_suite="tests",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ])
