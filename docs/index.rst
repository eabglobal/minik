.. minik documentation master file, created by
   sphinx-quickstart on Tue Feb 19 14:49:40 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to minik's documentation
=================================

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
        name = app.current_request.query_params.get('name')

        # With the values defined in the object above this will return.
        # {'hello': 'me'}
        return {action: name}


Just like with any other lambda function you are responsible for provisioning the
API Gateway and for associating the lambda function with the gateway endpoint. Minik
is just the framework that allows you to write your api in a straight-forward fashion.

Motivation
**********

The team behind this framework is adopting a very minimal set of features to enhance
and streamline web development in the serverless space. These were the business
needs that encouraged us to build minik:

- I need to have the ability to write an API using a syntax I'm familiar with
  (flask like) in the AWS ecosystem.
- I want to decide how to build and deploy my lambda functions. I do not want
  my framework to dictate these processes for me. I want to own them!
- When installing my framework, I want to get only the framework. I don’t want
  to any additional tooling or any additional process-based workflows..
- When using the microframework I am aware that I am responsible for the configuration
  required to associate my lambda function to its endpoints.


The features of this library should be absolutely driven by a very specific
business need. So far, the minimal approach has been sufficient for our team to
write and expose and API using AWS services.

Just the framework
******************

Things to be aware of when working with minik:

- When used in your lambda function, you're responsible for including the source
  code of minik in your .zip artifact. For packaging purposes we recommend using
  `Juniper`_.
- Unlike other frameworks like Flask or Django where using the decorator is
  sufficient to define the routes of the web app, in minik, you’re responsible
  for linking a lambda function to the API gateway. We recommend using a
  `SAM`_ template.
- There is no local development server! For testing purposes, deploy the lambda
  in AWS! There's no excuse not to. Use `sam package` and `sam deploy` for deployment
  purposes.


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
