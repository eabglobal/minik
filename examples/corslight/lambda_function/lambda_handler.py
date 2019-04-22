from minik.core import Minik
from minik.status_codes import codes
from minik.models import Response


app = Minik()


@app.get("/beers")
def get_beers():

    app.response.headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date",
        "Authorization": "X-Api-Key,X-Amz-Security-Token"
    }

    return ', '.join(beer_list)


@app.get("/beers/{name}")
def get_beer(name: str):

    if name not in beer_list:
        app.response.status_code = codes.not_found
        return {'error': 'Beer not found'}

    return {'data': beer_list[name]}


beer_list = {
    "Aguila": {'id': '0'},
    "Arnold Palmer Spiked Half & Half": {'id': '1'},
    "Barmen": {'id': '2'},
    "Blue Moon": {'id': '3'},
    "Cape Line Sparkling Cocktails": {'id': '4'},
    "Colorado Native": {'id': '5'},
    "Coors Banquet": {'id': '6'},
    "Coors Light": {'id': '7'},
    "Coors Non Alcoholic": {'id': '8'},
    "Crispin Cider": {'id': '9'},
    "Cristal": {'id': '10'}
}
