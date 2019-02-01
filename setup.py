from setuptools import setup, find_packages


setup(name='minik',
      version='0.1',
      description='',
      author='EAB tech',
      author_email='eabtech@eab.com',
      packages=find_packages(),
      include_package_data=True,
      test_suite="tests",
      setup_requires=["pytest-runner"],
      tests_require=["pytest"])
