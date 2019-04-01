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

gh-pages:
	git checkout gh-pages
	rm -rf _images _sources _static
	git checkout master docs examples assets
	$(MAKE) -C docs html
	mv -fv docs/_build/html/* ./
	rm -rf docs examples assets
	git add -A
	git commit -m "Generated gh-pages"
	git push origin gh-pages
	git checkout master


release:
	python3 setup.py sdist bdist_wheel
	twine check dist/*
	twine upload dist/*

test-release:
	python3 setup.py sdist bdist_wheel
	twine check dist/*
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +