#!/usr/local/bin/python3
# coding: utf-8

__author__ = "Benny <benny.think@gmail.com>"

import logging
import os
import re
import traceback
from typing import Any, Union

from pyrogram import Client, filters, types, raw
from tgbot_ping import get_runtime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s [%(levelname)s]: %(message)s')

# Ortam değişkenlerinden değerleri al
PROXY = os.getenv("PROXY")
TOKEN = os.getenv("8367063788:AAH5vRd58qg2VGlw0rMQjPVhWC2jJhxkl_E")   # ✅ Bot token buradan okunacak
APP_ID = os.getenv("APP_ID", "21194358")
APP_HASH = os.getenv("APP_HASH", "9623f07eca023e4e3c561c966513a642")

# Telegram veri merkezi haritası
DC_MAP = {
    1: "Miami",
    2: "Amsterdam",
    3: "Miami",
    4: "Amsterdam",
    5: "Singapore"
}

def create_app():
    _app = Client("idbot", APP_ID, APP_HASH, bot_token=TOKEN)
    if PROXY:
        _app.proxy = dict(
            scheme="socks5",
            hostname=PROXY.split(":")[0],
            port=int(PROXY.split(":")[1])
        )
    return _app


app = create_app()
service_count = 0


def get_user_detail(user: "Union[types.User, types.Chat]") -> "str":
    global service_count
    service_count += 1
    if user is None:
        return "Gizli forward bilgisi alınamıyor!"

    return f"""
kullanıcı adı: `@{user.username} `
isim: `{user.first_name or user.title}`
soyisim: `{user.last_name}`
id: `{user.id}`

bot mu?: {getattr(user, "is_bot", None)}
DC: {user.dc_id} {DC_MAP.get(user.dc_id, "")}
dil kodu: {getattr(user, "language_code", None)}
telefon numarası: {getattr(user, "phone_number", None)}
    """


def get_channel_detail(channel) -> "str":
    global service_count
    service_count += 1
    return f"""
Kanal/grup detayları:

kullanıcı adı: `@{channel.chats[0].username} `
başlık: `{channel.chats[0].title}`
id: `-100{channel.chats[0].id}`
    """


@app.on_message(filters.command(["start"]))
def start_handler(client: "Client", message: "types.Message"):
    chat_id = message.chat.id
    client.send_message(chat_id, "Benny'nin ID botuna hoş geldiniz.")


@app.on_message(filters.command(["help"]))
def help_handler(client: "Client", message: "types.Message"):
    chat_id = message.chat.id
    text = """Mesajları forward edin, kullanıcı adı gönderin veya /getme ile kendi hesabınızı öğrenin.\n
    Açık kaynak: https://github.com/tgbot-collection/IDBot
    """
    client.send_message(chat_id, text)


@app.on_message(filters.command(["getme"]))
def getme_handler(client: "Client", message: "types.Message"):
    me = get_user_detail(message.from_user)
    message.reply_text(me, quote=True)


@app.on_message(filters.command(["ping"]))
def ping_handler(client: "Client", message: "types.Message"):
    logging.info("Pong!")
    chat_id = message.chat.id
    runtime = get_runtime("botsrunner_idbot_1")
    global service_count
    if getattr(message.chat, "username", None) == "BennyThink":
        msg = f"{runtime}\n\nServis sayısı: {service_count}"
    else:
        msg = runtime
    client.send_message(chat_id, msg)


@app.on_message(filters.command(["getgroup"]))
def getgroup_handler(client: "Client", message: "types.Message"):
    me = get_user_detail(message.chat)
    message.reply_text(me, quote=True)


@app.on_message(filters.text & filters.group)
def getgroup_compatibly_handler(client: "Client", message: "types.Message"):
    text = message.text
    if getattr(message.forward_from_chat, "type", None) == "channel" or not re.findall(r"^/getgroup@.*bot$", text):
        logging.warning("bu bir kanal forward'ı ya da komut değil")
        return

    logging.info("uyumlu getgroup çağrısı")
    getgroup_handler(client, message)


@app.on_message(filters.forwarded & filters.private)
def forward_handler(client: "Client", message: "types.Message"):
    fwd = message.forward_from or message.forward_from_chat
    me = get_user_detail(fwd)
    message.reply_text(me, quote=True)


def get_users(username):
    user: "Union[types.User, Any]" = app.get_users(username)
    return get_user_detail(user)


def get_channel(username):
    peer: "Union[raw.base.InputChannel, Any]" = app.resolve_peer(username)
    result = app.invoke(
        raw.functions.channels.GetChannels(
            id=[peer]
        )
    )
    return get_channel_detail(result)


@app.on_message(filters.text & filters.private)
def private_handler(client: "Client", message: "types.Message"):
    username = re.sub(r"@+|https://t.me/", "", message.text)
    funcs = [get_users, get_channel]
    text = ""

    for func in funcs:
        try:
            text = func(username)
            if text:
                break
        except Exception as e:
            logging.error(traceback.format_exc())
            text = e

    message.reply_text(text, quote=True)


if __name__ == '__main__':
    app.run()
