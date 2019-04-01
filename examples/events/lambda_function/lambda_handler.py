from minik.core import Minik
app = Minik()


@app.route("/events/{zip_code}", methods=['GET'])
def get_events(zip_code: int):

    print(f'{type(zip_code)} - {zip_code}')
    if zip_code == 20902:
        return {'events': ['MD Gran fondo', 'Old Busthead']}

    return {'events': ['other events']}


@app.route("/events", methods=['POST'])
def post_event():

    event_name = app.current_request.json_body.get('name')
    # Save this event somewhere

    return {'id': 100, 'name': event_name}
