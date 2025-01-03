from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, TwitchAPIException
from flask import Flask, redirect, request

TARGET_SCOPE = [AuthScope.CHAT_READ]

app = Flask(__name__)
twitch: Twitch
auth: UserAuthenticator


@app.route('/login')
def login():
    return redirect(auth.return_auth_url())


@app.route('/login/confirm')
async def login_confirm():
    state = request.args.get('state')
    if state != auth.state:
        return 'Bad state', 401
    code = request.args.get('code')
    if code is None:
        return 'Missing code', 400
    try:
        token, refresh = await auth.authenticate(user_token=code)
        await twitch.set_user_authentication(token, TARGET_SCOPE, refresh)
    except TwitchAPIException as e:
        return 'Failed to generate auth token', 400
    return 'Sucessfully authenticated!'


async def twitch_setup(APP_ID, APP_SECRET, APP_REDIRECT_URI, PORT):
    global twitch, auth
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, TARGET_SCOPE, url=APP_REDIRECT_URI)
    app.run(host="0.0.0.0", port=PORT)
