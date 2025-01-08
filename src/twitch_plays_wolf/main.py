import asyncio
from os import environ
import logging

from twitch_plays_wolf.twitch import TwitchPlaysWolf
from twitch_plays_wolf.wolf import WolfAPI
from twitch_plays_wolf.api import app

from dataclasses import dataclass
from aioemit import Emitter

@dataclass(frozen=True)
class GlobalState:
    wolf: WolfAPI = None
    twitch: TwitchPlaysWolf = None


def main():
    APP_ID = environ.get('APP_ID')
    APP_SECRET = environ.get('APP_SECRET')
    APP_REDIRECT_URI = environ.get('APP_REDIRECT_URI')
    PORT = environ.get('PORT', 5000)
    WOLF_SOCKET_PATH = environ.get('WOLF_SOCKET_PATH')

    if not all([APP_ID, APP_SECRET, APP_REDIRECT_URI, PORT, WOLF_SOCKET_PATH]):
        missing_keys = [key for key, value in locals().items() if value is None]
        raise EnvironmentError(f"Missing environment variables: {missing_keys}")

    logging.basicConfig(level=logging.DEBUG)

    event_bus = Emitter()

    state = GlobalState(
        wolf=WolfAPI(event_bus, WOLF_SOCKET_PATH),
        twitch=TwitchPlaysWolf(event_bus, APP_ID, APP_SECRET, APP_REDIRECT_URI)
    )
    asyncio.run(state.twitch.create())

    app.config['STATE'] = state
    asyncio.run(app.run(host="0.0.0.0",
                        port=PORT))


if __name__ == "__main__":
    main()
