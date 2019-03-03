Getting started
===============

As a web developer building serverless APIs in the AWS ecosystem, there are two
core services that one must be familiar with:

- `API Gateway <https://aws.amazon.com/api-gateway/>`_
- `AWS Lambda function <https://aws.amazon.com/lambda/>`_

In this domain, API gateway serves as the proxy that receives a request from the
internet, validates it and sends the request to the associated function or view
for processing.

Setup
*****

    >>> pip install minik

After installing minik, you can write your lambda function handler using a familiar
interface. Your `lambda_handler.py` should look like:

.. code:: python

    from minik.core import Minik
    app = Minik()

    @app.route("/events/{zip_code}", methods=['GET'])
    def get_events(zip_code):

        if zip_code == '20902':
            return {'events': ['MD Gran fondo', 'Old Busthead']}

        return {'events': ['other events']}

    @app.route("/events", methods=['POST'])
    def post_event():

        event_name = app.current_request.json_body.get('name')
        # Save this event somewhere

        return {'id': 100}

This API definition creates an instance of Minik and stores that instance in a
variable called app. With the app, you can then decorate your views in a Flask
like fashion.

If you were to put that snippet in the AWS Lambda console, you would have to
set the `entrypoint` to be the `lambda_handler.app`. However, for the above
definition to work as expected you *must* include minik as one of your dependencies.
Minik must be included in the .zip artifact you upload to the lambda function.

SAM template
************

With the lambda function handler in place, the `SAM` template for our function
would looks like:

.. code-block:: yaml

    Transform: 'AWS::Serverless-2016-10-31'
    Resources:

    EventHandler:
        # This resource creates a Lambda function.
        Type: 'AWS::Serverless::Function'

        Properties:
            # This function uses the python 3.6 runtime.
            Runtime: python3.6

            # This is the Lambda function's handler.
            Handler: lambda_handler.app

            # The location of the Lambda function code.
            CodeUri: ./dist/events.zip

            # Event sources to attach to this function. In this case, we are attaching
            # one API Gateway endpoint to the Lambda function. The function is
            # called when a HTTP request is made to the API Gateway endpoint.
            Events:

                GetEventsApi:
                    # Define an API Gateway endpoint that responds to HTTP GET at /events/20901
                    Type: Api
                    Properties:
                        Path: /events/{zip_code}
                        Method: GET

                AddEventApi:
                    # Define an API Gateway endpoint that responds to HTTP POST at /events/20902
                    Type: Api
                    Properties:
                        Path: /events/{zip_code}
                        Method: POST


The first line makes this cloudformation template a SAM template. In the definition
of the lambda function, the `Handler` field points to the Minik app as defined in
the `lambda_function:lambda_handler.py`. This configuration means that Minik will be
the handler of the (event, context) you receive from the API gateway.

The Events section of the template defines the API Gateway endpoints. The entries
in this section are what link an API endpoint to a lambda function. In this case
the template defines two endpoints linked to the same function.

Packaging
*********
Our SAM template refers to the CodeUri: ./dist/events.zip, this is the artifact
that will be deployed to AWS and it must contain the code dependencies as well
as the lambda function definition. The AWS documentation describes the steps that
a developer can take in order to create that artifact `here <https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html>`_.

We recomend a tool called `Juniper`_ as a way to generate the .zip artifact. With
Juniper you have to create a manifest file that defines your packaging structure.
In this example that file would look like this:

.. code:: yaml

    functions:
      events:
        requirements: ./src/requirements.txt
        include:
        - ./src/lambda_function.py

    >>> pip install juniper
    >>> juni build

After running the juni build command, by default juniper creates a zip artifact
in the dist directory. The zip file will contain the dependencies of the
project. In this case the only dependency we have is minik.

Deployments
***********
To deploy our function to AWS, make sure you have the `SAM cli`_ installed. Using
SAM, we have two commands at our disposal, one for packaging and one for deployment.

.. code:: python

    sam package \
        --s3-bucket serverless-artifacts \
        --template-file ./sam.yml \
        --output-template-file ./dist/new_sam.yml

The sam package command will upload the .zip artifact to the bucket you specify
as an input parameter and the command will generate an identical transformed verison
of the template in the destination you identify.

.. code:: python

    sam deploy \
        --template-file ./dist/new_sam.yml \
        --stack-name minik-sample-api \
        --capabilities CAPABILITY_IAM \
        --region us-east-1


The deploy command takes as an input the transformed version generated by the package
command and it actually creates a new stack in your AWS domain.

Conclusion
**********
The previous sections outlined the entire workflow a developer must follow in order
to build APIs using AWS resources. The process outlined above gives the developer
the flexibility to structure the project however he/she desires. Also, the developer
has full ownership of the packaging and deployment processes.

Minik is a bridge between the API Gateway and the lambda function. The bridge gives
the developer a familiar interface to streamline the development of serverless APIs.

Working example
***************

The codebase for minik includes an examples directory. The snippets shown here
have been tested and deployed using the services, tools and best practices defined
in this page. To run the examples:

    >>> git clone https://github.com/eabglobal/minik.git
    >>> cd minik
    >>> python3 -m venv venv
    >>> source venv/bin/activate
    >>> pip install -r requirements/dev.txt
    >>> cd examples/events

Once you're in this folder, you can use the commands defined in the make file.

    >>> make build
    >>> make package AWS_PROFILE=<your profile>
    >>> make deploy AWS_PROFILE=<your profile>

.. _`SAM cli`: https://github.com/awslabs/aws-sam-cli
.. _`Juniper`: https://github.com/eabglobal/juniper
