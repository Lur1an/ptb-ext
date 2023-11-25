import asyncio
import logging
from typing_extensions import override
from telegram.constants import ParseMode

from telegram.ext import ExtBot


class ErrorForwarder(logging.Handler):
    def __init__(
        self,
        bot: ExtBot,
        chat_ids: list[int],
        log_levels: list[str] = ["WARN", "ERROR"],
    ):
        super().__init__()
        self._bot = bot
        self._chat_ids = chat_ids
        self._log_levels = log_levels
        self._loop = asyncio.get_event_loop()

    @override
    def emit(self, record):
        try:
            formatted = self.format(record)
            formatted = formatted.replace("`", "'")
            msg = "```\n" + formatted + "\n```"
            if record.levelname in self._log_levels:
                for chat_id in self._chat_ids:
                    f = self._bot.send_message(
                        chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2
                    )
                    asyncio.run_coroutine_threadsafe(f, self._loop)
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            self.handleError(record)
