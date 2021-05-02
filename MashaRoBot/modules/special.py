#created by @am_dq_fan #do_not edit moduls 

from io import BytesIO
from time import sleep
from typing import Optional, List
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot, User
from telegram import ParseMode
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown
from MashaRoBot.modules.helper_funcs.chat_status import is_user_ban_protected, user_admin

import random, re
import telegram
import MashaRoBot.modules.sql.users_sql as sql
from MashaRoBot import dispatcher, OWNER_ID, DEV_USERS, DRAGONS, LOGGER
from MashaRoBot.modules.helper_funcs.filters import CustomFilters
from MashaRoBot.modules.disable import DisableAbleCommandHandler

USERS_GROUP = 4

MESSAGES = (
    "ഓരോ കനവിലും, ഓരോ നിനവിലും .നിന്നോർമകൾ ഒരു നറുതെന്നലായി,നിറയുന്നു എന്നുള്ളിൽആയിരം ജന്മദിനാശംസകൾ ",
    "കളിയും ചിരിയും കുറുബും കുസുത്രിയും കൈനിറഞ്ഞു തന്ന കൂടൂക്കാരന് ഒരായിരം ജന്മദിനാശംസകൾ ",
    "eppozum ninte chirikkunna mugam ennum ente manassil undu . ennum oru chankai eppozum evideyum kanum HAPPY BIRTHDAY DEAR. FEND ",
    "ആകാശത്ത് രേവതി നക്ഷത്രം ഉതിക്കുമ്പോൾ മഴപെയ്യുകയാണെങ്കിൽ , അ മഴതുള്ളി ചിപ്പിയിൽ വീണാൽ അത് മുത്തായി തീരും , നിന്റെ പിറന്നാൾ ദിനത്തിൽ രേവതി നക്ഷത്രം ഉതിക്കുമ്പോൾ മഴക്കുവേണ്ടി ഞാനും പ്രാർതിക്കും ഒരു ചിപ്പിയെപോലെ , പിറന്നാൾ ആശംസകൾ ",
    "1000 janmamagilu kathirikum ninne nagn orma than peelikal nokki orthirikkum ninne nagnnee varunna vasantha naalathanete Janmma Naali ",
    "നിങ്ങളും നിങ്ങളുടെ അത്ഭുതകരമായ ഊരർജ്ജവും ഇല്ലാതെ എന്റെ ജീവിതം ഒന്നുമല്ല . ഇന്നും എപ്പോഴും നിങ്ങൾക്ക് സന്തോഷം നേരുന്നു. Happy born today ",
    "നിങ്ങൾ അർഹിക്കുന്ന എല്ലാ സ്നേഹവും വിജയവും കൊണ്ട് നിങ്ങളുടെ മുന്നോട്ടുള്ള പാത നിറയട്ടെ. നിങ്ങൾ എനിക്കായി ചെയ്ത എല്ലാത്തിനും നന്ദി.Wish You a Happy Birthday..",
    "നിങ്ങളുടെ സ്നേഹമില്ലാത്ത ജീവിതം അർത്ഥശൂന്യമായിരിക്കും. ഞങ്ങളുടെ അവിശ്വസനീയമായ സാഹസങ്ങൾക്ക് ഞാൻ എന്നും നന്ദിയുള്ളവനാണ്. ജന്മദിനാശംസകൾ!Wish You a Happy Birthday..",
    "ഞാൻ വരുന്നതിനുമുമ്പ് മെഴുകുതിരികൾ കത്തിക്കരുത്! ജന്മദിനാശംസകൾ, ഇന്ന് രാത്രി കാണാം!Wish You a Happy Birthday",
    "anshi dq de vaka happy janichosam chinke 🥰🥰❤️❤️", 
)


@run_async
def snipe(bot: Bot, update: Update, args: List[str]):
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError as excp:
        update.effective_message.reply_text("Please give me a chat to echo to!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            update.effective_message.reply_text("Couldn't send the message. Perhaps I'm not part of that group?")


@run_async
def getlink(bot: Bot, update: Update, args: List[int]):
    message = update.effective_message
    if args:
        pattern = re.compile(r'-\d+')
    else:
        message.reply_text("You don't seem to be referring to any chats.")
    links = "Invite link(s):\n"
    for chat_id in pattern.findall(message.text):
        try:
            chat = bot.getChat(chat_id)
            bot_member = chat.get_member(bot.id)
            if bot_member.can_invite_users:
                invitelink = bot.exportChatInviteLink(chat_id)
                links += str(chat_id) + ":\n" + invitelink + "\n"
            else:
                links += str(chat_id) + ":\nI don't have access to the invite link." + "\n"
        except BadRequest as excp:
                links += str(chat_id) + ":\n" + excp.message + "\n"
        except TelegramError as excp:
                links += str(chat_id) + ":\n" + excp.message + "\n"

    message.reply_text(links)


@run_async
def slist(bot: Bot, update: Update):
    message = update.effective_message
    text1 = "My sudo users are:"
    text2 = "My support users are:"
    for user_id in DEV_USERS:
        try:
            user = bot.get_chat(user_id)
            name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
            if user.username:
                name = escape_markdown("@" + user.username)
            text1 += "\n - {}".format(name)
        except BadRequest as excp:
            if excp.message == 'Chat not found':
                text1 += "\n - ({}) - not found".format(user_id)
    for user_id in DRAGONS:
        try:
            user = bot.get_chat(user_id)
            name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
            if user.username:
                name = escape_markdown("@" + user.username)
            text2 += "\n - {}".format(name)
        except BadRequest as excp:
            if excp.message == 'Chat not found':
                text2 += "\n - ({}) - not found".format(user_id)
    message.reply_text(text1 + "\n", parse_mode=ParseMode.MARKDOWN)
    message.reply_text(text2 + "\n", parse_mode=ParseMode.MARKDOWN)


@run_async
@user_admin
def birthday(bot: Bot, update: Update, args: List[str]):
    if args:
        username = str(",".join(args))
    for i in range(5):
        bdaymessage = random.choice(MESSAGES)
        update.effective_message.reply_text(bdaymessage + username)


__help__ = """
*Owner only:*
- /getlink *chatid*: Get the invite link for a specific chat.
*Sudo only:*
- /quickscope *chatid* *userid*: Ban user from chat.
- /quickunban *chatid* *userid*: Unban user from chat.
- /snipe *chatid* *string*: Make me send a message to a specific chat.
*Admin only:*
- /birthday *@username*: Spam user with birthday wishes.
"""

__mod_name__ = "Special"

SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True, filters=CustomFilters.sudo_filter)
GETLINK_HANDLER = CommandHandler("getlink", getlink, pass_args=True, filters=Filters.user(OWNER_ID))
SLIST_HANDLER = CommandHandler("slist", slist, filters=Filters.user(OWNER_ID))
BIRTHDAY_HANDLER = CommandHandler("birthday", birthday, pass_args=True, filters=Filters.group)

dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(SLIST_HANDLER)
dispatcher.add_handler(BIRTHDAY_HANDLER)
