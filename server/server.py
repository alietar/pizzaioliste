from aiohttp import web
import aiosqlite
import asyncio
import json
import datetime
from typing import Any, AsyncIterator, Awaitable, Callable, Dict
import discordBot
import sys

from database import DataBase


if len(sys.argv) < 2:
    absolute_path = "./"
else:
    absolute_path = sys.argv[1]


if len(sys.argv) < 3:
    port = 8000
else:
    port = sys.argv[2]


sos_path = absolute_path + "assets/sos.json"
credentials_path = absolute_path + "assets/credentials.json"
db_path = absolute_path + "assets/database.db"
website_path = absolute_path + "../website/"


with open(credentials_path) as f:
    _file_content = json.load(f)
    credential = _file_content["admin_password"]
    webhook_url = _file_content["discord_webhook_url"]
    discord_token = _file_content["discord_token"]

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


async def respond(incoming_request, content = {}, status = 200):
    headers, encoded_content = generate_headers(content)

    response_request = web.Response(headers=headers, status=status)

    await response_request.prepare(incoming_request)
    await response_request.write(encoded_content)

    return response_request


routes = web.RouteTableDef()

@web.middleware
async def print_incoming_request(request, handler):
    print(f"Incoming {request.method} request -> {request.rel_url}")

    return await handler(request)




##### Add middle man to print incoming requests


### Get a list of the available SOS

@routes.get("/api/student")
async def available_sos(request):
    print("Sending the list of available SOS")

    sos_list = {}

    for idx, value in sos.items():
        sos_list[int(idx)] = value["name"]

    return await respond(request, content=sos_list)


### Get a list of the asked SOS from the students

@routes.get('/api/admin')
async def asked_sos(request):
    response_content = {}
    status = 200

    # Checks the credential
    if request.headers["Credential"] != credential:
        status = 401

    else:
        db = request.config_dict["DB"]
        sos_list = await db.get_all_sos()

        response_content = {"format": ["id", "Création", "Prénom", "Nom", "Email", "Sos ID", "SOS Description", "Horaire", "Bat", "Turne", "Fait 0Non, 1Oui"], "sos": sos_list}

    return await respond(request, content=response_content, status=status)


### Cors request

#@routes.options('/api')
#async def cors_options(request):
#    return await respond(request)



### Add a SOS to the database

@routes.post('/api/student')
async def add_sos(request):
    content = await request.json()
    response_content = {}
    status = 200
    db = request.config_dict["DB"]

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

        form = [
            str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")), # order_date
            content["fname"], # first name
            content["lname"], # last name
            content["email"], # email
            int(content["sos"]), # sos id
            sos[content["sos"]]["name"], # sos name
            content["timeslot"], # timeslot
            content["bat"], # bat
            int(content["nb"]), # turne
            "pending" # is the sos done
        ]


        # Checks if the client didn't already ordered two sos for the same day
        asked_day = datetime.datetime.strptime(form[6], '%Y-%m-%dT%H:%M').weekday() # form[6] is the timeslot of the ordered sos
        has_reached_limit = await db.check_user_limit(form[3], asked_day) # form[3] is the email from the form

        if has_reached_limit:
            raise Exception("Two SOS are already ordered for this day")

        # Adding sos request to the database
        _id = await db.add_sos(form)

        form.append(_id)

        print("Added SOS to the database")

        # Send message on discord
        request.config_dict["Send_Queue"].put_nowait(form)


    except Exception as e:
        print("An exception occurred")
        print(e)

        response_content = {"error": str(e)}
        status = 400


    return await respond(request, content=response_content, status=status)


async def init_db(app: web.Application) -> AsyncIterator[None]:
    db = DataBase(path_to_db=db_path)
    await db.connect()
    app["DB"] = db
    yield
    await app["DB"].close()


async def init_bot(app: web.Application) -> AsyncIterator[None]:
    app["Send_Queue"] = asyncio.Queue()
    app["Modify_Queue"] = asyncio.Queue()

    bot = discordBot.Bot(app["Send_Queue"], app["Modify_Queue"])
    task1 = asyncio.create_task(bot.start(discord_token))
    task2 = asyncio.create_task(app["DB"].modify_loop(app["Modify_Queue"]))

    yield

    task1.cancel()
    task2.cancel()


async def root_handler(request):
    return web.HTTPFound('/index.html')


async def init_app() -> web.Application:
    app = web.Application(middlewares=[print_incoming_request])
    app.add_routes(routes)
    app.router.add_route('*', '/', root_handler)
    app.router.add_static("/", website_path)
    app.cleanup_ctx.append(init_db)
    app.cleanup_ctx.append(init_bot)

    return app


if __name__ == "__main__":
    web.run_app(init_app(), port=port)
