.. minik documentation master file, created by
   sphinx-quickstart on Tue Feb 19 14:49:40 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Minik - Serverless Web Framework
================================

|circle| |pypi version| |apache license|

Minik is a python microframework used to write clean APIs in the serverless domain.

As a developer working in AWS, if you would like to have full control of your development
process while having access to a familiar interface, minik is the framework for you.
To build your first API using minik, SAM and Juniper go to :doc:`quickstart`.

Familiar interface
******************

.. code:: python

    from minik.core import Minik
    app = Minik()

    @app.route("/test/{proxy}")
    def hello(proxy):
        return {"Hello": proxy}

HTTP Methods
************
With minik you can also specify the HTTP methods for a given view. If you don't
define the methods, every single HTTP method will be allowed by default.

.. code-block:: python

    from minik.core import Minik

    app = Minik()

    @app.route('/events/{location}')
    def events_view(location: str):
        # This route will be invoked for GET, POST, PUT, DELETE...
        return {'data': ['granfondo MD', 'Silver Spring Century']}

    @app.route('/events', methods=['POST', 'PUT'])
    def create_event_view():
        create_event(app.request.json_body)
        return {'result': 'complete'}

The microframework also includes a set of convenient decorator methods for the
case in which a view is associated with a single HTTP method.

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


Route Validation
****************
Using the `function annotations`_, you can specify the type of value you are expecting
in your route. The added advantage is that minik will convert your parameter to the
appropriate type. For instance:

.. code:: python

    @app.route('/articles/{author}/{year}/')
    def get_articles_view(author: str, year: int):
        assert isinstance(author, str) and isinstance(year, int)
        return {'author_name': author, 'year': year}

If you need to specify a regular expression:

.. code-block:: python

    from minik.fields import ReStr

    @app.route('/item/{item_id}/', methods=['GET'])
    def get_item(item_id: ReStr(r'([0-9a-f]{8}$)')):
        assert isinstance(item_id, str)
        return {'id': item_id}

You can extend our validation framework and write your own classes for route fields!

.. code-block:: python

    from minik.fields import BaseRouteField

    class RouteTracker(BaseRouteField):

        def validate(self, value):
            return value in ('fitbit', 'nikeplus', 'vivosmart',)


    @app.route('/tracker/{name}/', methods=['GET'])
    def get_tracker_info(name: RouteTracker):
        assert isinstance(name, str)
        return {'name': name}

In the example above, your view will only be executed when the name paramter passed in
matches one of the trackers specified in the validator. All you need to do is implement the
validation logic. To learn more checkout out the `features`_ page.

.. _`function annotations`: https://www.python.org/dev/peps/pep-3107/
.. _`features`: https://eabglobal.github.io/minik/features.html

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
Things to be aware of when working with minik:

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


Minik in λ
**********
When working with a lambda function as the handler of a request from the API gateway.
If the endpoint is configured to use the pass-through lambda integration, your function
will have to be defined as follows:

.. code:: python

    def lambda_handler(event, context):
        # Business logic! Get values out of the event object.
        return {
            'statusCode': 200,
            'headers': 'response headers',
            'body': 'response body'
        }

In this approach, the event your lambda function receives from the gateway looks
like this:

.. code:: json

    {
        "path": "/test/hello",
        "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, lzma, sdch, br",
            "..."
        },
        "pathParameters": {
            "proxy": "hello"
        },
        "requestContext": {
            "accountId": "123456789012",
            "resourceId": "us4z18",
            "stage": "test",
            "requestId": "41b45ea3-70b5-11e6-b7bd-69b5aaebc7d9",
            "..."
            "resourcePath": "/{proxy+}",
            "httpMethod": "GET",
            "apiId": "wt6mne2s9k"
        },
        "resource": "/{proxy+}",
        "httpMethod": "GET",
        "queryStringParameters": {
            "name": "me"
        },
        "stageVariables": {
            "stageVarName": "stageVarValue"
        }
    }

Without Minik, every single API endpoint you write will need to parse that object
as a way to get the data values you care about. The entire scope of the object is
documented `here <https://docs.aws.amazon.com/lambda/latest/dg/eventsources.html#eventsources-api-gateway-request>`_.

With Minik, you get a clear familiar interface that hides the complexity of dealing
with the raw representation of the event and context objects. We take care of parsing
the API gateway object for you, so that you can focus on writing your business logic.
Using the above object and endpoint as an example, our lambda function would instead be:

.. code:: python

    from minik.core import Minik
    app = Minik()

    @app.route("/test/{action}")
    def hello(action):
        name = app.request.query_params.get('name')

        # With the values defined in the object above this will return.
        # {'hello': 'me'}
        return {action: name}


Just like with any other lambda function you are responsible for provisioning the
API Gateway and for associating the lambda function with the gateway endpoint. Minik
is just the framework that allows you to write your api in a straight-forward fashion.


.. _SAM: https://github.com/awslabs/serverless-application-model
.. _Chalice: https://github.com/aws/chalice
.. _Serverless: https://serverless.com/
.. _Juniper: https://github.com/eabglobal/juniper

.. |circle| image:: https://circleci.com/gh/eabglobal/minik/tree/master.svg?style=shield
    :target: https://circleci.com/gh/eabglobal/minik/tree/master

.. |pypi version| image:: https://img.shields.io/pypi/v/minik.svg
    :target: https://pypi.org/project/minik/

.. |apache license| image:: https://img.shields.io/github/license/eabglobal/minik.svg
    :target: https://github.com/eabglobal/minik/blob/master/LICENSE

Contents:
=========

.. toctree::
    :maxdepth: 2
    :numbered:
    :glob:

    quickstart.rst
    features.rst
