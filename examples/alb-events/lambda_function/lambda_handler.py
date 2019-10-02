from minik.core import Minik

app = Minik()


@app.get("/events")
def get_events():
    return {"data": [{'zip_code': 20902}, {'zip_code': 73071}]}


@app.post("/events")
def post_event():

    event_name = app.request.json_body.get('name')
    # Save this event somewhere
    return {'id': 100, 'name': event_name}


@app.get("/events/{zip_code}")
def get_event(zip_code: int):

    print(f'{type(zip_code)} - {zip_code}')
    if zip_code == 20902:
        return {'events': ['MD Gran fondo', 'Old Busthead']}

    return {'events': ['other events']}


@app.route("/events/{event_id}")
class EventAPI:

    def on_get(self, request, response, *, event_id: str):
        return {'id': 12}

    def on_post(self, request, response, *, event_id: str):
        return {'created': True}
