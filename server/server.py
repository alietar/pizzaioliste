from aiohttp import web
import aiosqlite
import json
import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable, Dict
import sqlite3

db_file_name = "form.db"

sos_path = 'sos.json'

def get_sos(path):
    _sos = []

    with open(path) as f:
        _sos = json.load(f)

    return _sos

sos = get_sos(sos_path)



routes = web.RouteTableDef()

@routes.get('/')
async def handler(request):
    return web.Response(status=501)


@routes.options('/')
async def cors_options(request):
    print("-> Cors request")

    headers = {
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Origin': 'http://localhost:8000',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        "Access-Control-Allow-Headers": "X-Requested-With, Content-type"
    }

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


        # Checking if the client did not already order 2 sos the same day
        async with db.execute(
            "SELECT timeslot FROM orders WHERE email = ?", [form[3]]
        ) as cursor:
            timeslots = await cursor.fetchall()
            days = []

            sos_day = datetime.datetime.strptime(form[6], '%Y-%m-%dT%H:%M').weekday()

            for timeslot in timeslots:
                date_timeslot = datetime.datetime.strptime(timeslot[0], '%Y-%m-%dT%H:%M')
                days.append(date_timeslot.weekday())

            if days.count(sos_day) >= 2:
                raise Exception("Two SOS are already ordered for this day")


    except Exception as e:
        print("An exception occurred")
        print(e)

        response_content = {"error": str(e)}
        status = 400


    json_string = json.dumps(response_content)
    encoded_string = json_string.encode(encoding='utf_8')

    headers = {
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Origin': 'http://localhost:8000',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        "Access-Control-Allow-Headers": "X-Requested-With, Content-type",
        "Content-Type": "application/json",
        "Content-Length": str(len(encoded_string))
    }

    resp = web.Response(headers=headers, status=status)
    await resp.prepare(request)
    await resp.write(encoded_string)

    # Return if the sos order isn't valid
    if status == 400:
        return resp


    # Adding sos request to the database

    async with db.execute("""
        INSERT INTO orders (order_date,
                            fname,
                            lname,
                            email,
                            sos,
                            sos_name,
                            timeslot,
                            bat,
                            turne,
                            done) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", form,
    ) as cursor:
        _id = cursor.lastrowid
    await db.commit()

    print(_id)

    # Responds to the client
    return resp



def get_db_path() -> Path:
    return db_file_name


async def init_db(app: web.Application) -> AsyncIterator[None]:
    db = await aiosqlite.connect(get_db_path())
    #db.row_factory = aiosqlite.Row Not Useful?
    app["DB"] = db
    yield
    await db.close()


async def init_app() -> web.Application:
    app = web.Application()
    app.add_routes(routes)
    app.cleanup_ctx.append(init_db)

    return app


def try_make_db() -> None:
    db_path = get_db_path()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            order_date DATETIME,
            fname TEXT,
            lname TEXT,
            email TEXT,
            sos INTEGER,
            sos_name TEXT,
            timeslot DATETIME,
            day INT,
            bat TEXT,
            turne INTEGER,
            done BOOLEAN)
        """
        )

        conn.commit()




if __name__ == "__main__":
    try_make_db()
    web.run_app(init_app(), port=8100)
