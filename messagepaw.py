import slack
from slack.errors import SlackApiError
import os
import json
import re
import logging
from pathlib import Path
from dotenv import load_dotenv

# logging.basicConfig(
#     level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
# )

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

client = slack.WebClient(token=os.getenv("BOT_TOKEN"))

users = client.users_list()["members"]

data = {}


def get_users():
    for user in users:
        if (
            not user["deleted"]
            and not user["is_bot"]
            and re.search("America", user["tz"]) is None
        ):
            data[user["real_name"]] = {
                "id": user["id"],
                "pur": "0",
            }


def get_pur():
    with open("pur.json", "r") as f:
        pur = json.load(f)
    for user in data:
        if user in pur:
            data[user]["pur"] = pur[user]


def create_json():
    with open("clear_users.json", "w") as f:
        json.dump(data, f, indent=4, separators=(",", ": "))


def send_message(user_id, message):
    try:
        response = client.chat_postMessage(channel=user_id, text=message)
        logging.debug(f"Message sent to {user_id}: {response}")
    except SlackApiError as e:
        logging.debug(f"Error sending message: {e.response['error']}")


if __name__ == "__main__":
    get_users()
    get_pur()
    create_json()

    with open("clear_users.json", "r") as f:
        data = json.load(f)
    for user in data:
        if 0 < int(data[user]["pur"]) < 95:
            message = f"""

Привет!

Заметил, что твой PUR за прошлый месяц (PUR - соотношение между прод временем в табличке Canvas Task & Time и времени записанном в метадате на работах) немного ниже значения, что мы ожидаем.

Данные:

- Твой PUR - {data[user]["pur"]}%
- Ожидаемый PUR - 95%

Пожалуйста обрати внимание на этот показатель в текущем месяце. Если значение будет слишком низким, мы вынуждены будем оплачивать ЗП лишь по Active time с Insightful.


Автор бота: <@U05HCBAPKKM> (Отпишитесь мне в личку пришло ли вам сообщение :slightly_smiling_face:) Если возникнут вопросы, пиши)
"""
            send_message(data[user]["id"], message)
