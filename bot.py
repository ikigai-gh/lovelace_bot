#!/usr/bin/env python

import asyncio
import logging
import sys
import os
from typing import Any, Dict

from aiogram import Bot, Dispatcher, Router, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import lovelace as lv

try:
    TOKEN = os.environ["TG_TOKEN"]
    ADMIN_ID = int(os.environ["TG_ADMIN_ID"])
except (KeyError, TypeError):
    logging.error("TG_TOKEN and TG_ADMIN_ID must be specified!")
    sys.exit(1)

form_router = Router()

class Form(StatesGroup):
    name = State()
    age = State()
    city = State()
    text = State()


@form_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.name)
    await message.answer(f"Hello, what's your name?")

""" All bot's commands """

@form_router.message(Command("list"), F.from_user.id == ADMIN_ID)
async def command_list_handler(message: Message) -> None:
    users = lv.get_users()
    user_info = "\n".join([str(u) for u in users])
    await message.answer(user_info)

@form_router.message(Command("ban"), F.from_user.id == ADMIN_ID)
async def command_ban_handler(message: Message) -> None:
    user_id = message.text.split()[1]
    lv.ban_user(user_id)
    await message.answer(f"User {user_id} banned")

@form_router.message(Command("search"))
async def command_search_handler(message: Message) -> None:
    # TODO: Use class instance instead of the tuple
    user_is_active = bool(lv.get_user(message.from_user.id)[7])

    if user_is_active:
        users = lv.search(message.from_user.id)
        user_info = "\n".join([str(u) for u in users])
        await message.answer(f"Found some nerds: ")
        await message.answer(user_info)
    else:
        await message.answer(f"Account is deactivated")

@form_router.message(Command("deactivate"))
async def command_deactivate_handler(message: Message) -> None:
    lv.deactivate_user(message.from_user.id)
    await message.answer(f"Deactivated")

@form_router.message(Command("activate"))
async def command_activate_handler(message: Message) -> None:
    lv.activate_user(message.from_user.id)
    await message.answer(f"Activated")

""" All bot's states """

@form_router.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer(f"How old are you?")

@form_router.message(Form.age)
async def process_age(message: Message, state: FSMContext) -> None:
    await state.update_data(age=int(message.text))
    await state.set_state(Form.city)
    await message.answer(f"Where are you from?")

@form_router.message(Form.city)
async def process_city(message: Message, state: FSMContext) -> None:
    await state.update_data(city=message.text)
    await state.set_state(Form.text)
    await message.answer(f"Tell me about yourself")

@form_router.message(Form.text)
async def process_text(message: Message, state: FSMContext) -> None:
    form_data = await state.update_data(text=message.text)
    await state.clear()
    await create_user(message=message, data=form_data)

""" CRUD """

async def create_user(message: Message, data: Dict[str, Any]):
    data["photo"] = "null"
    data["tg_id"] = message.from_user.id
    lv.create_user(**data)
    await message.answer(f"User {data['name']} created")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
