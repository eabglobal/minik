from setuptools import setup, find_packages

__author__ = 'Pedro Diaz'

setup(name='minik',
      version='0.1',
      description='',
      author='EAB tech',
      author_email='eabtech@eab.com',
      packages=find_packages(),
      test_suite="tests",
      setup_requires=["pytest-runner"],
      tests_require=["pytest"])
