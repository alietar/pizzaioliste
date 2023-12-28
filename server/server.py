from aiohttp import web
import aiosqlite
import json
import datetime
from typing import Any, AsyncIterator, Awaitable, Callable, Dict

from database import DataBase

sos_path = "assets/sos.json"
credentials_path = "assets/credentials.json"
db_path = "assets/database.db"

with open(credentials_path) as f:
    _file_content = json.load(f)
    credential = _file_content["admin_password"]
    webhook_url = _file_content["discord_webhook_url"]

with open(sos_path) as f:
    sos = json.load(f)



def generate_headers(data = {}):
    json_string = json.dumps(data)
    encoded_data = json_string.encode(encoding='utf_8')

    headers = {
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Origin': 'http://localhost:8000',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        "Access-Control-Allow-Headers": "X-Requested-With, Content-type, Credential",
        "Content-Type": "application/json",
        "Content-Length": str(len(encoded_data))
    }

    return headers, encoded_data


routes = web.RouteTableDef()

@routes.get('/')
async def handler(request):
    print(f"-> SOS request from {request.host}")

    response_content = {}
    status = 200
    form = []
    db = request.config_dict["DB"]

    try:
        if request.headers["Credential"] == credential:
            print("Client requests the SOS")
        else:
            raise Exception("Credentials are incorrect")


        lines = await db.get_all_sos()

        response_content = {"format": ["id", "Création", "Prénom", "Nom", "Email", "Sos ID", "SOS Description", "Horaire", "Bat", "Turne", "Fait 0Non, 1Oui"], "sos": lines}


    except Exception as e:
        print("An exception occurred")
        print(e)

        response_content = {"error": str(e)}
        status = 400

    headers, data = generate_headers(response_content)

    resp = web.Response(headers=headers, status=status)
    await resp.prepare(request)
    await resp.write(data)

    # Return if the sos order isn't valid
    if status == 400:
        return resp

    return resp



@routes.options('/')
async def cors_options(request):
    print("-> Cors request")

    headers, data = generate_headers()

    return web.Response(headers=headers)


@routes.post('/')
async def add_sos(request):
    print(f"-> SOS request from {request.host}")

    content = await request.json()
    response_content = {}
    status = 200
    form = []
    db = request.config_dict["DB"]

    print(content)

    # Try to get informations from the form, if it fails then the data is incorrect
    try:
        if content["confirmation"] != "y":
            raise Exception("Conditions aren't accepted")

        if not (content["bat"] in "ABCDE"):
            raise Exception("Bat is not A, B, C, D or E")

        if not content['nb'].isdecimal():
            raise Exception("Turne is not a valid integer")

        if not content["sos"].isdecimal() and int(content["sos"]) >= len(sos):
            raise Exception("SOS is not a valid integer")

        # Implement email verification

        print('Form is valid')


        form.append(str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))) # order_date
        form.append(content["fname"]) # first name
        form.append(content["lname"]) # last name
        form.append(content["email"]) # email
        form.append(int(content["sos"])) # sos id
        form.append(list(sos.keys())[form[4]]) # sos name
        form.append(content["timeslot"]) # timeslot
        form.append(content["bat"]) # bat
        form.append(int(content["nb"])) #turne
        form.append(False)


        # Checks if the client didn't already ordered two sos for the same day
        asked_day = datetime.datetime.strptime(form[6], '%Y-%m-%dT%H:%M').weekday() # form[6] is the timeslot of the ordered sos
        has_reached_limit = await db.check_user_limit(form[3], asked_day) # form[3] is the email from the form

        if has_reached_limit:
            raise Exception("Two SOS are already ordered for this day")


    except Exception as e:
        print("An exception occurred")
        print(e)

        response_content = {"error": str(e)}
        status = 400

    headers, data = generate_headers(response_content)

    resp = web.Response(headers=headers, status=status)
    await resp.prepare(request)
    await resp.write(data)

    # Return if the sos order isn't valid
    if status == 400:
        return resp


    # Adding sos request to the database
    await db.add_sos(form)

    # Responds to the client
    return resp


async def init_db(app: web.Application) -> AsyncIterator[None]:
    db = DataBase()
    await db.connect()
    app["DB"] = db
    yield
    await app["DB"].close()


async def init_app() -> web.Application:
    app = web.Application()
    app.add_routes(routes)
    app.cleanup_ctx.append(init_db)

    return app


if __name__ == "__main__":
    web.run_app(init_app(), port=8100)
















"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import json

### Needs to check the host


sos = ["Lorem", "Ipsum", "Dolor", "Sit", "Amet"]




def add_sos(form):
    send_sos(form)


def send_sos(form):
    description = f"Prénom : {form['fname']}\nNom : {form['lname']}\nBat : {form['bat']}\nTurne : {form['nb']}"

    data = {
        "content": "Nouvelle demande de SOS",
        "embeds": [{
            "title": form["sos_name"],
            "description": description,
            "color": 2326507,
            "author": {
                "name": form["email"]
            },
            "footer": {
                "text": "Pas de demande particulière"
            },
            "timestamp": "2023-12-11T23:00:00.000Z"
        }]
    }

    print(data)


    result = requests.post(url, json = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
"""
