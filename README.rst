Minik: Serverless Web Framework
===============================

.. image:: assets/minik.png

Time to move on from our ASGI based frameworks. Using AWS lambda functions
and API Gateway, minik will serve as the framework that facilitates development
in the serverless space.

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
define the methods, by default, every single HTTP method will be allowed.

.. code-block:: python

    from minik.core import Minik

    app = Minik()

    @app.route('/events/{location}')
    def events_view(location):
        # This route will be invoked for GET, POST, PUT, DELETE... Any request.
        return {'data': ['granfondo MD', 'Silver Spring Century']}

    @app.route('/events', methods=['POST', 'PUT'])
    def create_event_view():
        create_event(app.request.json_body)
        return {'result': 'complete'}


The Basic Idea
**************

The primary concept here is to bring the niceties web developers are familiar with
to a cloud native domain. Borrowing from the syntax adopted by `Flask` using minik
should give any developer a very familiar feeling. The only difference is that
instead of dealing with WSGI and web servers in the conventioal sense of the word,
we're now dealing with two AWS services.

Conceptually, the idea of having a request/response objects encapsulated by a nice
framework apply here.

- Setting `resp.text` sends back unicode, while setting `resp.content` sends back bytes.
- Setting `resp.media` sends back JSON/YAML (`.text`/`.content` override this).
- Case-insensitive `req.headers` dict (from Requests directly).
- `resp.status_code`, `req.method`, `req.url`, and other familiar friends.

Why?
****

It was time to build Yet Another Web Framework YAWF. This time, the team is adopting
a very minimal set of features to enhance and streamline web development in the
serverless space. The scope of this framework is limited in scope to receive json
requests from an API Gateway endpoint and it will respond using json. That's it!

The features of this library should be absolutely driven by a very specific
business need. So far, the minimal approach has been sufficient for our team to
write and expose and API using AWS services.

What?
*****

A web framework built out of the frustrations and roadblocks the team encountered
while working with `Chalice`. The main advantages of this implementation over the
current frameworks in this domain are the following:

- Batteries **not** included! This is just the framework, nothing more, nothing else.
- Ability to leverage the domain knowledge of working with Flask or Django.
- Minimal set of features driven to solve a very specific problem.

Limitations!
************

As previously stated, this framework was built as a way to replace `Chalice` and
as such, it implements a very minimal set of features.

Things to be aware of when working with this library:

- When used in your lambda function, you're responsible of including the source
  code of minik in your .zip artifact. For packaging purposes we recommend using
  `juniper <https://github.com/eabglobal/juniper>`_.
- Unlike other frameworks like `Flask` or `Django` where using the decorator is
  sufficient to define the routes of the web app. In minik, you're responsible for
  linking a lambda function to a the API gateway. We recommend using a `SAM template`_.
- There is not local development server! For testing purposes, deploy the lambda
  in AWS! There's no excuse not to.

- Only supports request response in json format!

Getting started
===============

For a new project, when making a decision as to what 'web framework' to adopt for
a given use case. Working with AWS resources, there are two main components that
a developer must have certain familiarity with:

- `API Gateway <https://aws.amazon.com/api-gateway/>`_
- `AWS Lambda function <https://aws.amazon.com/lambda/>`_

In this domain, API gateway serves as the proxy that receives a request from the
internet, validates it and sends the request to the associated function or view
for processing. The lambda function encapsulates the business logic that must
be executed when a request is received.

In the serverless domain, it is best practice to use a `CloudFormation` template
as the blueprint of the resources your app will be using. When working with serverless
resources (API Gateway, lambda functions and dynamo tables) using a `SAM template`_
is best practice. SAM is just an extension to cloudformation that facilitates the definition
and wiring of these resources.

.. _SAM template: https://github.com/awslabs/serverless-application-model

Sam template
************

This is what a sample SAM.yml template looks like:

.. code-block:: yaml

    Transform: 'AWS::Serverless-2016-10-31'
    Resources:

    HelloHandler:
        # This resource creates a Lambda function.
        Type: 'AWS::Serverless::Function'

        Properties:

        # This function uses the python 3.6 runtime.
        Runtime: python3.6

        # This is the Lambda function's handler.
        Handler: app.app

        # The location of the Lambda function code.
        CodeUri: ./src

        # Event sources to attach to this function. In this case, we are attaching
        # one API Gateway endpoint to the Lambda function. The function is
        # called when a HTTP request is made to the API Gateway endpoint.
        Events:

            ThumbnailApi:
                # Define an API Gateway endpoint that responds to HTTP GET at /hello
                Type: Api
                Properties:
                    Path: /hello/{name}
                    Method: GET


The very first line is the one that differentiates this template from a regular
cloud formation definition. Specifically for using `minik`, the Handler field
defines a file called `app.py` with a variable called app. Just as defined the
`Simple Example` section.

The last piece of the puzzle is encapsulated in the events section of the file.
That section defines the API gateway endpoint that will be created for the `/hello`
endpoint. Where the `hello_view` is the function that will be called when the route
is executed.

Building the SAM template is a responsibility of the developer. This tool does not
manipulate the template at all. The template is what links an API Gateway endpoint
to a lambda function.

Contributing
************

For guidance on setting up a development environment and how to make a
contribution to Minik, see the `contributing guidelines`_.

.. _contributing guidelines: https://github.com/eabglobal/minik/blob/master/CONTRIBUTING.rst

Links
*****

* Documentation: https://eabglobal.github.io/minik/
* License: `Apache Software License`_

* Code: https://github.com/eabglobal/minik
* Issue tracker: https://github.com/eabglobal/minik/issues
* Test status:

  * Linux, Mac: https://circleci.com/gh/eabglobal/minik

.. _Apache Software License: https://github.com/eabglobal/minik/blob/master/LICENSE
