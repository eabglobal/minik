from minik.core import Minik

app = Minik()

req_type_by_name = {
    'api_request': 'API Gateway!',
    'alb_request': 'ALB!'
}


@app.get("/events")
def get_events():
    """
    The view handler for the `/events` route, this function will return an html
    response with a list of events. Each event points to another route to get
    more information on the event.

    This view will also display the request type based on the service that invoked
    the lambda function. Minik supports request from API Gateway and Application
    Load Balancer natively.
    """

    app.response.headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date",
        "Authorization": "X-Api-Key,X-Amz-Security-Token"
    }

    req_type = req_type_by_name.get(app.request.request_type)

    return f"""
    <html>
        <head>
            <title>Hello from {req_type}</title>
        </head>
        <body>
            <h1>Hello from {req_type}</h1>
            <a href="/events/20902">Silver Spring Events</a>
            <a href="/events/32608">Alachua County Events</a>
        </body>
    </html>"""


@app.get("/events/{zip_code}")
def get_event(zip_code: int):
    """Very simple handler that returns a json response based on the zip code."""

    if zip_code == 20902:
        return {'events': ['MD Gran fondo', 'Old Busthead']}

    return {'events': ['other events']}


@app.post("/events/{zip_code}")
def post_event(zip_code: int):
    """ An echo function to return the body and zip of the request."""
    # Store a new event
    return {'zip_code': zip_code, 'post_data': app.request.json_body}
