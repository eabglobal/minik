.. currentmodule:: minik

Minik Changelog
===============

Version 0.1.5
-------------

Released on February 25th, 2019, codename Yunus

- Minor updates to the pypi definition
- Initial version of the project's documentation (minik/issues/9).
- Implemented feature that allows definition a view for a given (path, http_method)
  pair (minik/issues/11).


Version 0.1.4
-------------

Released on February 8th, 2019, codename Gran Fondo II

- Initial implementation to support method definition in the route (minik/issues/7)
- Included the http codes from the requests library. This is a convenience mapping
  between different http status codes and their names.
- Updated the examples in the READ me to reflect the new functionality.


Version 0.1.3
-------------

Released on February 5th, 2019, codename Gran Fondo I

- Fix bug in the JsonReponse header (minik/issues/5)
- Minor updates to the README document


Version 0.1.1
-------------

Released on January 28th 2019, codename Fondo

- First public preview release.
- Absolute bare minimum set of features to parse a request from API gateway
- Framework acceps application/json content types and it will respond in json