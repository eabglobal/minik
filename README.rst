Minik: Serverless Web Framework
===============================

.. image:: assets/minik.png

|circle| |pypi version| |apache license|

Using AWS lambda functions and API Gateway, minik will serve as the framework
that facilitates development in the serverless space.

Installing
**********

Install the latest release:

>>> pip install minik
✨🍰✨

Only **Python 3.6+** is supported.

Simple Example
**************
In it's most basic form; quite honestly, it's only form. This is how your lambda
function should look like:

.. code-block:: python

    from minik.core import Minik, BadRequestError

    app = Minik()

    @app.route('/hello/{name}')
    def hello_view(name):

        if name == 'FINDME':
            # Returns a 400 status code with the message as the body.
            raise BadRequestError(msg='This is not a supported name.')

        # A simple way of getting the current request as json.
        request_payload = app.request.json_body
        return {'hello': name}

HTTP Methods
************
With minik you can also specify the HTTP methods for a given view. If you don't
define the methods, every single HTTP method will be allowed by default.

.. code-block:: python

    from minik.core import Minik

    app = Minik()

    @app.route('/events/{location}')
    def events_view(location):
        # This route will be invoked for GET, POST, PUT, DELETE...
        return {'data': ['granfondo MD', 'Silver Spring Century']}

    @app.route('/events', methods=['POST', 'PUT'])
    def create_event_view():
        create_event(app.request.json_body)
        return {'result': 'complete'}


Route Parameter Validation
**************************
Minik uses `function annotations`_ to validate the value of a route. If the type
of an expected parameter is not valid, minik will respond with a 404 not found
status code.

.. code:: python

    @app.route('/articles/{author}/{year}/')
    def get_articles_view(author: str, year: int):
        # Type conversion: isinstance(author, str) and isinstance(year, int)
        return {'author_name': author, 'year': year}


To learn more checkout out the `route validation`_ page.

.. _`function annotations`: https://www.python.org/dev/peps/pep-3107/
.. _`route validation`: https://eabglobal.github.io/minik/features


Motivation
**********
The team behind this framework is adopting a very minimal set of features to enhance
and streamline web development in the serverless space. These were the business
needs that encouraged us to build minik:

- Ability to write an API using a familiar (Flask like) syntax using serverless
  services.
- Flexibility on how to build and deploy lambda functions. I do not want
  my framework to dictate these processes for me. I want to own them!
- When installing a web framework, I want to get only the framework. I don’t
  want any additional tooling or any additional process-based workflows.
- When using the microframework I am responsible for the configuration
  required to associate my lambda function to its endpoints.

The features of this library should be absolutely driven by a very specific
business need. So far, the minimal approach has been sufficient for our team to
write and expose an API using AWS services.


Just the framework
******************
Things to be aware of when working using minik:

- When used in your lambda function, you're responsible for including the source
  code of minik in your .zip artifact. For packaging purposes we recommend using
  `Juniper`_.
- Unlike other frameworks like Flask or Django, where using the decorator is
  sufficient to define the routes of the web app, in minik, you’re responsible
  for linking a lambda function to the API gateway. We recommend using a
  `SAM`_ template.
- Minik does not include a local development server! For testing purposes, you can
  either deploy your lambda to AWS using `sam package` and `sam deploy`. For local
  deployment purposes you can use `sam local`.

Quickstart
**********
Minik is just one of the pieces that you need to build serverless APIs. If you
are curious to learn more about best practices and how to get started with this
microframework, checkout out `getting started <https://eabglobal.github.io/minik/quickstart.html>`_
guide.

The quickstart uses a very simple example, which is included in this codebase, as
a way to highlight the benefits of the framework.

Contributing
************

For guidance on setting up a development environment and how to make a
contribution to Minik, see the `contributing guidelines`_.

.. _contributing guidelines: https://github.com/eabglobal/minik/blob/master/CONTRIBUTING.rst
.. _Juniper: https://github.com/eabglobal/juniper
.. _SAM: https://aws.amazon.com/serverless/sam/

Links
*****

* Documentation: https://eabglobal.github.io/minik/
* License: `Apache Software License`_

* Code: https://github.com/eabglobal/minik
* Issue tracker: https://github.com/eabglobal/minik/issues
* Test status:

  * Linux, Mac: https://circleci.com/gh/eabglobal/minik

.. _Apache Software License: https://github.com/eabglobal/minik/blob/master/LICENSE

.. |circle| image:: https://circleci.com/gh/eabglobal/minik/tree/master.svg?style=shield
    :target: https://circleci.com/gh/eabglobal/minik/tree/master

.. |pypi version| image:: https://img.shields.io/pypi/v/minik.svg
    :target: https://pypi.org/project/minik/

.. |apache license| image:: https://img.shields.io/github/license/eabglobal/minik.svg
    :target: https://github.com/eabglobal/minik/blob/master/LICENSE
