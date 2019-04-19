from minik.core import Minik
from minik.models import Response
app = Minik()


@app.get("/events")
def get_as_text():

    return Response(
        headers={
            "Content-Type": "text/html; charset=utf-8",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date",
            "Authorization": "X-Api-Key,X-Amz-Security-Token"
        },
        body='there are two events'
    )


@app.get("/events/{zip_code}")
def get_events(zip_code: int):

    print(f'{type(zip_code)} - {zip_code}')
    if zip_code == 20902:
        return {'events': ['MD Gran fondo', 'Old Busthead']}

    return {'events': ['other events']}


@app.post("/events")
def post_event():

    event_name = app.current_request.json_body.get('name')
    # Save this event somewhere

    return {'id': 100, 'name': event_name}
