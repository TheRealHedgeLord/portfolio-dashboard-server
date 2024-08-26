from clients.http import HTTPClient
from utils import CachedClass


class TelegramBot(HTTPClient, metaclass=CachedClass):
    _name = "Telegram"
    _base_url = "https://api.telegram.org"
    _request_limit = 0.1

    def __init__(self, bot_token: str) -> None:
        super().__init__()
        self._bot_token = bot_token

    async def send_message(
        self, chat_id: str, message: str, parse_mode: str = "html"
    ) -> None:
        return await self._call(
            "get",
            f"/bot{self._bot_token}/sendMessage",
            parameters={"chat_id": chat_id, "parse_mode": parse_mode, "text": message},
        )

    async def get_update(self) -> dict:
        return await self._call(
            "get",
            f"/bot{self._bot_token}/getUpdates",
        )
