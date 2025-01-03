import asyncio
from os import environ

from twitch_plays_wolf.twitch import twitch_setup

def main():
    APP_ID = environ.get('APP_ID')
    APP_SECRET = environ.get('APP_SECRET')
    APP_REDIRECT_URI = environ.get('APP_REDIRECT_URI')
    PORT = environ.get('PORT', 5000)

    if not all([APP_ID, APP_SECRET, APP_REDIRECT_URI, PORT]):
        raise EnvironmentError("Required environment variables are not set")

    asyncio.run(twitch_setup(APP_ID, APP_SECRET, APP_REDIRECT_URI, PORT))


if __name__ == "__main__":
    main()