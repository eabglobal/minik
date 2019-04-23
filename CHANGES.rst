.. currentmodule:: minik

Minik Changelog
===============

Version 0.4.0
-------------

Released on April 22nd, 2019, codename Yunus III

- Large refactoring effort to make minik more flexible (issues/29)
  - Using middleware to build a request for a given event
  - Using middleware to handle server errors
  - Using middleware to handle exceptions

- Exposing the response object to the view to enable custom headers and
  content-types (issues/10)

- Adding debug mode to control whether an exception trace should be sent to
  a consumer (issues/24)

Version 0.3.0
-------------

Released on March 31st, 2019, codename Yunus II

- Implemented route validation feature (issues/13)

- Updated version of the documentation and README


Version 0.2.0
-------------

Released on March 17nd, 2019, codename Yunus I

- First version of documentation is done!

- Added badges to the README and Documentation


Version 0.1.7
-------------

Released on February 25th, 2019, codename Yunus

- Minor updates to the pypi definition
- Initial version of the project's documentation (minik/issues/9).
- Implemented feature that allows definition a view for a given (path, http_method)
  pair (minik/issues/11).
- Updating readme to be less verbose


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