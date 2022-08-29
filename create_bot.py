import logging

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import config
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.token, parse_mode='markdownv2')
dp = Dispatcher(bot, storage=storage)
 