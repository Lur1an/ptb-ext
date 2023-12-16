import abc
from typing import Callable, Optional
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler
from pydantic import BaseModel
import telegram.ext.filters as tg_filters
from ptb_ext.types import HandlerFunction

class NextReplyEntrypoint(BaseModel, abc.ABC):
    prompt: str

class CommandEntrypoint(NextReplyEntrypoint):
    command: str

class CallbackEntrypoint(NextReplyEntrypoint):
    callback_data_type: str | type
    filters: tg_filters.BaseFilter = tg_filters.ALL

class MessageEntryPoint(NextReplyEntrypoint):
    filters: tg_filters.BaseFilter = tg_filters.ALL

def next_reply_handler(*, entry_point: NextReplyEntrypoint, cancel_command: str = "cancel") -> Callable[[HandlerFunction], ConversationHandler]:
    async def cancel(update: Update, _: CallbackContext):
        if message := update.message:
            await message.reply_text("Action cancelled.")
        return ConversationHandler.END

    prompt = entry_point.prompt
    async def prompter(update: Update, _: CallbackContext):
        if message := update.message:
            await message.reply_text(prompt)
        return 1

    def inner(f: HandlerFunction) -> ConversationHandler:
        match entry_point:
            case CommandEntrypoint(command=command, filters=filters):
                entry_points = [CommandHandler(command, callback=prompter, filters=filters)]
            case CallbackEntrypoint(pattern=pattern):
                entry_points = [CallbackQueryHandler(callback=prompter, pattern=pattern)]
            case MessageEntryPoint(filters=filters):
                entry_points = [MessageHandler(callback=prompter, filters=filters)]
            case _:
                raise NotImplementedError
        conversation = ConversationHandler(
            entry_points=entry_points, # type: ignore
            states = {
                1: [MessageHandler(callback=f, filters=tg_filters.TEXT)],
            },
            fallbacks=[CommandHandler(cancel_command, callback=cancel)],
        )
        return conversation
    return inner
