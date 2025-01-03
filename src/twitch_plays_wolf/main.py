import asyncio
from os import environ
import logging

from twitch_plays_wolf.twitch import twitch_setup, run_server, setup_wolf


def main():
    APP_ID = environ.get('APP_ID')
    APP_SECRET = environ.get('APP_SECRET')
    APP_REDIRECT_URI = environ.get('APP_REDIRECT_URI')
    PORT = environ.get('PORT', 5000)
    WOLF_SOCKET_PATH = environ.get('WOLF_SOCKET_PATH')
    TWITCH_STREAM_KEY = environ.get('TWITCH_STREAM_KEY')
    DOCKER_IMAGE = environ.get('DOCKER_IMAGE', "ghcr.io/games-on-whales/retroarch:edge")

    if not all([APP_ID, APP_SECRET, APP_REDIRECT_URI, PORT, WOLF_SOCKET_PATH, TWITCH_STREAM_KEY, DOCKER_IMAGE]):
        missing_keys = [key for key, value in locals().items() if value is None]
        raise EnvironmentError(f"Missing environment variables: {missing_keys}")

    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(twitch_setup(APP_ID, APP_SECRET, APP_REDIRECT_URI))
    asyncio.run(setup_wolf(WOLF_SOCKET_PATH, TWITCH_STREAM_KEY, DOCKER_IMAGE))
    asyncio.run(run_server(PORT))


if __name__ == "__main__":
    main()
