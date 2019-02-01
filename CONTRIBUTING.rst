How to contribute to Minik
============================

Thank you for considering contributing to Minik!

Reporting issues
----------------

- Describe what you expected to happen.
- If possible, include a `minimal, complete, and verifiable example`_ to help
  us identify the issue. This also helps check that the issue is not with your
  own code.
- Describe what actually happened. Include the full traceback if there was an
  exception.
- List your Python and Minik. If possible, check if this issue is already fixed
  in the repository.

.. _minimal, complete, and verifiable example: https://stackoverflow.com/help/mcve

Submitting patches
------------------

- Include tests if your patch is supposed to solve a bug, and explain
  clearly under which circumstances the bug happens. Make sure the test fails
  without your patch.
- Try to follow `PEP8`_, but you may ignore the line length limit if following
  it would make the code uglier.
- Keep in mind that minik is configured to use Flake8 for linting and the CI
  pipeline will fail for PEP8 related issues.

First time setup
~~~~~~~~~~~~~~~~

- Download and install the `latest version of git`_.
- Configure git with your `username`_ and `email`_::

        git config --global user.name 'your name'
        git config --global user.email 'your email'

- Make sure you have a `GitHub account`_.
- Fork Minik to your GitHub account by clicking the `Fork`_ button.
- `Clone`_ your GitHub fork locally::

        git clone https://github.com/{username}/minik
        cd minik

- Add the main repository as a remote to update later::

        git remote add minik https://github.com/eabglobal/minik
        git fetch minik

- Create a virtualenv::

        python3 -m venv env
        . env/bin/activate
        # or "env\Scripts\activate" on Windows

- Install Minik in editable mode with development dependencies::

        pip install -e ".[dev]"

.. _GitHub account: https://github.com/join
.. _latest version of git: https://git-scm.com/downloads
.. _username: https://help.github.com/articles/setting-your-username-in-git/
.. _email: https://help.github.com/articles/setting-your-email-in-git/
.. _Fork: https://github.com/eabglobal/minik/fork
.. _Clone: https://help.github.com/articles/fork-a-repo/#step-2-create-a-local-clone-of-your-fork

Start coding
~~~~~~~~~~~~

- Create a branch to identify the issue you would like to work on (e.g.
  ``2287-dry-test-suite``)
- Using your favorite editor, make your changes, `committing as you go`_.
- Try to follow `PEP8`_, but you may ignore the line length limit if following
  it would make the code uglier.
- Include tests that cover any code changes you make. Make sure the test fails
  without your patch. `Run the tests. <contributing-testsuite_>`_.
- Push your commits to GitHub and `create a pull request`_.
- Celebrate 🎉

.. _committing as you go: https://dont-be-afraid-to-commit.readthedocs.io/en/latest/git/commandlinegit.html#commit-your-changes
.. _PEP8: https://pep8.org/
.. _create a pull request: https://help.github.com/articles/creating-a-pull-request/

.. _contributing-testsuite:

Running the tests
~~~~~~~~~~~~~~~~~

Run the basic test suite with::

    pytest

This only runs the tests for the current environment.

Running test coverage
~~~~~~~~~~~~~~~~~~~~~

Generating a report of lines that do not have test coverage can indicate
where to start contributing. Run ``pytest`` using ``coverage`` and generate a
report on the terminal and as an interactive HTML document::

    python -m pytest --cov .
    coverage html
    # then open htmlcov/index.html

Read more about `coverage <https://coverage.readthedocs.io>`_.

Running the full test suite with ``tox`` will combine the coverage reports
from all runs.


Building the docs
~~~~~~~~~~~~~~~~~

Build the docs in the ``docs`` directory using Sphinx::

    make docs

Open ``docs/_build/html/index.html`` in your browser to view the docs.

When updating the docs, it is convenient to have a local server pick up the latest
changes in the documents. For this purposes phix is included in the dev dependencies.

    >>> cd docs
    >>> make html
    >>> phix -t html -p 8001
    # open the documentation at http://localhost:8001

Every changes you make to any .rst file inside the docs will trigger the rebuild
of the documentatation and the recreation of the html artifacts.

Read more about `Sphinx <https://www.sphinx-doc.org>`_.

make targets
~~~~~~~~~~~~

Minik provides a ``Makefile`` with various shortcuts. They will ensure that
all dependencies are installed.

- ``make test`` runs the basic test suite with ``pytest``
- ``make cov`` runs the basic test suite with ``coverage``
- ``make docs`` builds the HTML documentation
