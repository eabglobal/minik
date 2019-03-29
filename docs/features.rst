Route Validation
================
Defined as a web frameworks ability to execute a view based on the validity of the parameters
in the route. As an example consider this route definition `tenant/<uuid:tenant_uuid>/`
in this particular case, the view associated with this route should only be executed
if the tenant_uuid is a valid uuid.

For minik, this feature takes advantage of the `function annotations`_ features of
python. In this particular case, a developer must specify the type of value he/she
is expecting at the view level. In this case, the type of field expected is not
in the route, but instead it is part of the view signature. Using the previous route
as a basis, a route in minik looks like:

.. code-block:: python

    import uuid

    @app.route('tenant/{tenant_uuid}/')
    def get_tenant_info(tenant_uuid: uuid.UUID):
        return {'tenant': 'information'}

Note that in this case the tenant_uuid parameter in the view definition has a
specific type; uuid.UUID. Using the built in python uuid package, minik will try
to convert a given value to a uuid.UUID. If it succeeds, the converted value will
passed in as the view paramter. If the validation does not succeed, the view will
not be called and the response will be a 404, not found.

Regex Based Routes
******************
Minik comes with a built in mechanism that allows a developer to specify a regular
expression as the means to validate a given route parameter.

.. code-block:: python

    from minik.fields import ReStr

    @app.route('/item/{item_id}/')
    def get_item(item_id: ReStr(r'([0-9a-f]{8}$)')):
        assert isinstance(item_id, str)
        return {'id': item_id}

In this particular example, requests that match the given route with an item_id
that matches the regular expression will be handled. If a request comes in where
the item_id does not match the regex, a 404 not found response will be returned.

Keep in mind that you are responsible for enforcing the constraints of the regular
expression. For instance if the regex of the route above was ([0-9a-f]{8}); without
the $ at the end, partial matches in the route will pass in a valid. In this case
the regex is saying to accept a string where the first 8 characters have a constraint.

In this case, the type of value passed in to the view is NOT an instance of the
`ReStr` class, instead it is a string with the value.

Custom Route Fields
*******************
Minik exposes the built in mechamism used to implement the ReStr for a developer to
expand on the type of route parameters that a route can accept. Using a very simple
construct a developer can easily define what the validity logic of a route parameter.

.. code-block:: python

    from minik.fields import BaseRouteField
    class RouteTracker(BaseRouteField):

        def validate(self, value):
            return value in ('fitbit', 'nikeplus', 'vivosmart',)


    @sample_app.route('/tracker/{name}/', methods=['GET'])
    def get_tracker_info(name: RouteTracker):
        assert isinstance(name, str)
        return {'name': name}

The example above illustrates two constructs:

1. The definition of a custom route field
2. Usage of the route field in a view

This pattern is encouraged as it is a clear example of the single responsibility
principle. In this case, the RouteTracker's only responsibility is to determine if
a given name is valid or not. That's it!

Keep in mind that with a valid route, the value of field will be a string!

.. _`function annotations`: https://www.python.org/dev/peps/pep-3107/