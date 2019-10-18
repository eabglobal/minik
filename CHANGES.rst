.. currentmodule:: minik

Minik Changelog
===============

Version 0.5.3
-------------

Released on October 18th, 2019, codename Yeni Ridge.2

- Ignore 'return' from update_uri_parameters (by bafio)
  - When using type annotations, the return type annotation was included in the
    set of parameters. This is no longer the case.
  - Thanks to bafio for his contributions.


Version 0.5.1
-------------

Released on October 10th, 2019, codename Yeni Ridge

- Exposing the set of utility functions used to build the lambda events (issues/35)
  - Ability to create a sample API Gateway event
  - Ability to create a sample ALB event
  - These are the events a lambda function will receive when invoked by the
    respective service.


Version 0.5.0
-------------

Released on October 8th, 2019, codename Yeni Ridge

- Large refactoring effort to natively support requests from an ALB (issues/33)
  - Introducing a new router to keep track of the route/handler pairs
  - Refactoring the requests builders to correctly build a MinikRequest based
    on the event type (api_request, or alb_request)
  - Adding an example to associate a lambda function to an ALB (examples/alb-events)
  - Updating documentation.
- Updated the MinikRequest to keep the event received from the lambda function (issues/15).


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