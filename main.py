import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import random
import time
from aiohttp import web
import aiohttp_cors
import os
import threading
import datetime

now_cats = []


cred = credentials.Certificate("lab4_config.json")
firebase_admin.initialize_app(cred)

# These registration tokens come from the client FCM SDKs.
registration_tokens = [
    'd36W6hxtkb90YboQJ4T0Mk:APA91bHpQ8uMmo6fx1o1akomEXVZ6Qm6q_7ScuJYGY8eAFgiDxBq-QWr2sAJEcuIf1pCH2_dzsHla3JadnBONnFMQ3C7C0cVUQ1ffnHs4o4MrAonS2XvXnAknbnYnTAAi3V0Ahv-Cdjb',
    'dfCj9-l5G-2GUdl9iSedaK:APA91bEVg9ypr-Uve46NFPxQG4F-8Ak1m5cZb6jkYHoZUaNOEiEbUYpMNCzTiV2EOMDG7s9cbpHc4AikUvuQJKumSFAJ7_djbBU61WD_t3aILdUAxJvqPZaCZs0RpDUSoL6AZj35OqHv',
    'enPq8QQBxTqnmZgSGPgvkW:APA91bEqO4nVELFTp0HYLG6fUzvu6-aor-j7Iuwnjteo3BC9A8v0OaKthH9g8dECs1sqXU1zitNFtyU98EciKqK5rgFPJsxDfhANO_MBQhd0yOf7TUvsX9wlPAD30CG9NeOswU-Tz8df'
]

# Subscribe the devices corresponding to the registration tokens to the
# topic.
response = messaging.subscribe_to_topic(registration_tokens, "new_cat")
# See the TopicManagementResponse reference documentation
# for the contents of response.
print(response.success_count, 'tokens were subscribed successfully')

# my_notification = messaging.Notification(title="У нас новый кот!", body="У нас новый кот!", image="https://lh3.google.com/u/0/ogw/AAEL6si5OxViDmgZ09EmM2BRji0wiVSGZexwFbPCG3bp=s32-c-mo%22")


def append_new_cat():
    url = "https://api.thecatapi.com/v1/images/search"
    querystring = {"mime_types":"gif","api_key":"live_BupBzo4KWFAtkDAYyKz7a4BcK63I0OuL1Dr7kD2myJyPLVQWQEhNgCkPo4SSmC4s"}
    response = requests.request("GET", url, params=querystring)
    new_cat = {"time" : None, "url" : None}
    now = datetime.datetime.now()
    new_cat["time"] = now.strftime("%H:%M")
    new_cat["url"] = response.json()[0]['url']
    now_cats.append(new_cat)
    print(new_cat)
    message = messaging.Message(
        topic="new_cat"
    )
    response = messaging.send(message)
    print(response)

routes = web.RouteTableDef()

@routes.get('/get_cats')
async def get_daily_cats(request: web.Request):
    return web.json_response({"result" : now_cats})

app = web.Application()
app.add_routes(routes)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
})


# Configure CORS on all routes.
for route in list(app.router.routes()):
    cors.add(route)


def get_cats():
    while True:
        probability = random.random()
        if probability < 0.007:
            append_new_cat()
        time.sleep(60)


t2 = threading.Thread(target=get_cats)
t2.start()


append_new_cat()

web.run_app(app, port=os.getenv("PORT", default=5000))