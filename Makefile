.PHONY: all install-dev test coverage cov test-all tox docs release clean-pyc upload-docs ebook. From Flask

all: test

install-dev:
	pip install -q -e .[venv3]
	pip install -r requirements/dev.txt

test: clean-pyc
	python -m pytest --cov .

coverage: clean-pyc install-dev
	coverage run -m pytest
	coverage report
	coverage html

cov: coverage

test-all: install-dev
	tox

tox: test-all

docs: clean-pyc install-dev
	$(MAKE) -C docs html

release:
	python scripts/make-release.py

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +