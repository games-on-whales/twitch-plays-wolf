from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, TwitchAPIException, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
import logging


class TwitchPlaysWolf:
    def __init__(self, APP_ID, APP_SECRET, APP_REDIRECT_URI, TARGET_SCOPE=None):
        self.twitch = None
        self.chat = None
        self.auth = None
        self.target_channels = []
        self.APP_ID = APP_ID
        self.APP_SECRET = APP_SECRET
        self.APP_REDIRECT_URI = APP_REDIRECT_URI
        self.TARGET_SCOPE = TARGET_SCOPE or [AuthScope.CHAT_READ]

    async def create(self):
        self.twitch = await Twitch(self.APP_ID, self.APP_SECRET)
        self.auth = UserAuthenticator(self.twitch, self.TARGET_SCOPE, url=self.APP_REDIRECT_URI)

    def login_redirect_url(self):
        return self.auth.return_auth_url()

    async def login_confirm(self, state, code):
        if state != self.auth.state:
            return True, 'Bad state'
        if code is None:
            return True, 'Missing code'
        try:
            token, refresh = await self.auth.authenticate(user_token=code)
            await self.twitch.set_user_authentication(token, self.TARGET_SCOPE, refresh)
        except TwitchAPIException as e:
            return True, 'Failed to generate auth token'
        return False, ""

    async def chat_join(self, ready_event: EventData):
        logging.debug("Bot is ready to join channels")
        await ready_event.chat.join_room(self.target_channels)

    async def on_chat_message(self, msg: ChatMessage):
        logging.debug(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')

    async def chat_bot_setup(self, target_channel):
        if self.chat is None:
            self.chat = await Chat(self.twitch)
        else:
            self.chat.stop()

        self.target_channels.append(target_channel)
        # listen to when the bot is done starting up and ready to join channels
        self.chat.register_event(ChatEvent.READY, self.chat_join)
        # listen to chat messages
        self.chat.register_event(ChatEvent.MESSAGE, self.on_chat_message)
        self.chat.start()
        return True

    async def stop(self):
        if self.chat is not None:
            self.chat.stop()

        if self.twitch is not None:
            await self.twitch.close()
