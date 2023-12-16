from typing import Any, Callable, Coroutine

from telegram import Update
from telegram.ext import CallbackContext


HandlerFunction = Callable[[Update, CallbackContext], Coroutine]
