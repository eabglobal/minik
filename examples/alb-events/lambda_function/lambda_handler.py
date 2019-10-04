import json
from minik.core import Minik

app = Minik()

req_type_by_name = {
    'api_request': 'API Gateway!',
    'alb_request': 'ALB!'
}


@app.get("/events")
def get_events():
    app.response.headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date",
        "Authorization": "X-Api-Key,X-Amz-Security-Token"
    }
    headers = json.dumps(app.request.headers, indent=4)
    req_type = req_type_by_name.get(app.request.request_type)

    return f"""
    <html>
        <head>
            <title>Hello from {req_type}</title>
        </head>
        <body>
            <h1>Hello from{req_type}</h1>
            <h2>{headers}</h2>
        </body>
    </html>"""


@app.get("/events/{zip_code}")
def get_event(zip_code: int):

    print(f'{type(zip_code)} - {zip_code}')
    if zip_code == 20902:
        return {'events': ['MD Gran fondo', 'Old Busthead']}

    return {'events': ['other events']}
