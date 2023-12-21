import requests #dependency

url = "https://discord.com/api/webhooks/1184476140736348220/GSPo2_bmfbXKS2B3rA8bSsCUD_L6mtVTttyrIeySnTtY-oSB7ux0Bu_ZiKjGEdKbvp4R"

#for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
data = {
    "content" : "Ceci est un contenu",
    "username" : "Leonard de vinci"
}

#leave this out if you dont want an embed
#for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
data["embeds"] = [
    {
        "title" : "Test webhook",
        "description" : "testing webhook..."
    }
]

result = requests.post(url, json = data)

try:
    result.raise_for_status()
except requests.exceptions.HTTPError as err:
    print(err)
else:
    print("Payload delivered successfully, code {}.".format(result.status_code))
