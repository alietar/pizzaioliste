from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import json

### Needs to check the host


sos = ["Lorem", "Ipsum", "Dolor", "Sit", "Amet"]
url = "https://discord.com/api/webhooks/1184476140736348220/GSPo2_bmfbXKS2B3rA8bSsCUD_L6mtVTttyrIeySnTtY-oSB7ux0Bu_ZiKjGEdKbvp4R"




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


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()


    def do_POST(self):
        request_headers = self.headers
        length = int(request_headers.get('Content-Length'))
        content = json.loads(self.rfile.read(length).decode(encoding='utf_8'))

        print(content)

        error = ""

        # Try to get informations from the form, if it fails then the data is incorrect
        try:
            form = {}

            ### Verification of the form

            if content["confirmation"] != "y":
                raise Exception("Conditions aren't accepted")

            form["fname"] = content["fname"]
            form["lname"] = content["lname"]

            # Implement email verification
            form["email"] = content["email"]

            if not (content["bat"] in "ABCDE"):
                raise Exception("Bat is not A, B, C, D or E")

            form["bat"] = content["bat"]

            if not content['nb'].isdecimal():
                raise Exception("Turne is not a valid integer")

            form["nb"] = content["nb"]

            if not content['sos'].isdecimal():
                raise Exception("SOS is not a valid integer")

            form["sos_id"] = content["sos"]
            form["sos_name"] = sos[int(form["sos_id"])]

            print(form)

            add_sos(form)

            self.send_response(200)

        except Exception as e:
            print("An exception occurred")
            print(e)

            error = str(e)

            self.send_response(400)


        json_string = json.dumps({"error": error})
        print(json_string)
        encoded_string = json_string.encode(encoding='utf_8')

        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:8000')
        self.send_header("Content-type", "application/json")
        self.send_header("Content-length", str(len(encoded_string)))
        self.end_headers()

        self.wfile.write(encoded_string)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:8000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()


with HTTPServer(('', 8100), handler) as server:
    server.serve_forever()








