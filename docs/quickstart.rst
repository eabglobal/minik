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