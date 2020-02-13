Minik: Serverless Web Framework
===============================

.. image:: assets/minik.png

|circle| |pypi version| |apache license|

A web framework that facilitates the development of serverless applications using
AWS resources. Minik natively supports request from the API Gateway and the
Application Load Balancer.

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
    def hello_view(name: str):

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
    def events_view(location: str):
        # This route will be invoked for GET, POST, PUT, PATCH, DELETE...
        return {'data': ['granfondo MD', 'Silver Spring Century']}

    @app.route('/events', methods=['POST', 'PUT'])
    def create_event_view():
        create_event(app.request.json_body)
        return {'result': 'complete'}

If your view is associated with a single HTTP method, you can use the decorator
version.

.. code-block:: python

    from minik.core import Minik

    app = Minik()

    @app.get('/events/{location}')
    def get_view(location: str):
        return {'data': ['granfondo MD', 'Silver Spring Century']}

    @app.post('/events')
    def post_view():
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


Custom Headers
**************
To update the values of the HTTP response, minik exposes a response object at
the app level. By default minik will create a Response instance with a status code
of 200 and a set of default headers. The headers include a default content-type
value of `application/json`.

For instance, to set the CORS headers in a view and change the content type, a
view would look like:

.. code:: python

    app = Minik()

    @app.get('/articles/{author}/{year}/')
    def get_articles_view(author: str, year: int):
        app.response.headers = {
            "Content-Type": "Content-Type": "text/html; charset=utf-8",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date",
            "Authorization": "X-Api-Key,X-Amz-Security-Token"
        }

        return f"A very short article by {author}"


Debug Mode
**********
For unhandled exceptions, minik will respond with a 500 status code and
a generic error message. To get more details from the response including the stack
trace and information about the exception, run the app in debug mode.

By default the debug mode is set to False.

.. code:: python

    app = Minik(debug=True)

Initializing the app in debug mode will relay the stack trace back to the consumer.


ALB Support
***********
Along with having a native integration with the API Gateway, minik can now be used
to handle requests coming from an Application Load Balancer (ALB). The definition
of the web application is identical in both cases. There is no additional code required
to use minik with an ALB.

If a lambda function is the `target of an ALB`_, minik will parse the raw event,
find the view associated with the route and execute the view with the correct context.

.. code-block:: python

    from minik.core import Minik

    app = Minik()

    @app.get('/greetings')
    def get_greetings():
        app.response.headers = {"Content-Type": "text/html; charset=utf-8"}

        return """
        <html>
        <head>
            <title>Hello World!</title>
            <style>
            html, body {
            margin: 0; padding: 0;
            font-family: arial; font-weight: 700; font-size: 3em;
            text-align: center;
            }
            </style>
        </head>
        <body>
            <p>Hello World!</p>
        </body>
        </html>"""

Notice that there is nothing specific about the source that will eventually invoke
this lambda function. This codeblock can be used to handle a request either
from the API Gateway or from an ALB.

.. _`target of an ALB`: https://aws.amazon.com/blogs/networking-and-content-delivery/lambda-functions-as-targets-for-application-load-balancers/


Request Object
**************
Any view has access to the **app.request** instance as a way to retrieve the general
information of a request. The fields of this object include the query parameters,
the path parameters, headers, payload... Given that different sources might have
a set of additional fields, minik will store a copy of the original event in the
**app.request** instance.

For instance, the API Gateway has the concept of stage variables that is missing
from an event received from the ALB. In this case, the generic app.request instance will
not have a field called stage_variables. Instead, minik keeps a copy of the original
event and context objects in the request. In this case a developer can access these
values using the app.request.aws_event['StageVariables']. Where the aws_event is
the event minik received as the handler of the lambda function.

.. code-block:: python

    from minik.core import Minik

    app = Minik()

    @app.post('/events')
    def post_view():
        # app.request.json_body: The payload of a post request as a JSON object.
        # app.request.aws_event: The raw event sent by a source to the lambda function.
        # app.request.aws_context: The context of the lambda function.
        return {'result': 'complete'}


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
- Minik is service agnostic, as a web framework it natively supports requests
  from the API Gateway and an Application Load Balancer (ALB).
- Unlike other frameworks like Flask or Django, where using the decorator is
  sufficient to define the routes of the web app, in minik, you’re responsible
  for linking a lambda function to the API Gateway. We recommend using a
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
