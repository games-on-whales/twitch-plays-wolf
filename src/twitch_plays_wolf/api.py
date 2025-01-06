import logging

from flask import Flask, redirect, request, render_template
from twitch_plays_wolf.wolf import WolfAPI
from twitch_plays_wolf.twitch import TwitchPlaysWolf

app = Flask(__name__)


@app.route('/login')
def login():
    twitch: TwitchPlaysWolf = app.config['STATE'].twitch
    return redirect(twitch.login_redirect_url())


@app.route('/login/confirm')
async def login_confirm():
    twitch: TwitchPlaysWolf = app.config['STATE'].twitch
    (error, msg) = await twitch.login_confirm(request.args.get('state'), request.args.get('code'))
    if error:
        return msg, 400
    return render_template("main_control.html")


@app.route("/chat-bot/listen/", methods=['POST'])
async def chat_bot_start():
    twitch: TwitchPlaysWolf = app.config['STATE'].twitch
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    logging.debug(data)

    await twitch.chat_bot_setup(data["channel"])
    return "Chat bot starting...", 200


@app.route("/stream/start/", methods=['POST'])
async def start_stream():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    logging.debug(data)

    wolf: WolfAPI = app.config['STATE'].wolf
    wolf.add_app(data['docker_image'])
    wolf.create_session()
    wolf.start_session(data['twitch_stream_key'])

    return "Stream starting...", 200
