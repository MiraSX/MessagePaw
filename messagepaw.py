import slack
import os
import json
import re
import logging
from slack.errors import SlackApiError
from dotenv import load_dotenv
from sheetpaw import get_pur

logging.basicConfig(
    filename="sending_logs",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)


client = slack.WebClient(token=os.getenv("BOT_TOKEN"))


data = {}


def get_users():
    users = client.users_list()["members"]

    for user in users:
        if (
            not user["deleted"]
            and not user["is_bot"]
            and re.search("America", user["tz"]) is None
        ):
            data[user["profile"]["display_name"]] = user["id"]
    with open("./db/ctnt.json", "r") as f:
        data_ctnt = json.load(f)

    for key, value in data_ctnt.items():
        name_in_ctnt = value.get("Name")
        for data_key, data_value in data.items():
            if data_key == name_in_ctnt:
                value["ID"] = data_value

    for key, value in data_ctnt.copy().items():
        id_in_ctnt = value.get("ID")
        if id_in_ctnt is None:
            data_ctnt.pop(key)

    with open("./db/ctnt.json", "w") as f:
        json.dump(data_ctnt, f, indent=4, separators=(",", ": "))


def send_message(user_id, name, pur, message):
    try:
        response = client.chat_postMessage(channel=user_id, text=message)
        logging.info(
            f"Message sent to ID: {user_id} Name: {name} PUR: {pur}: {response.get('ok')}"
        )
    except SlackApiError as e:
        logging.info(f"Error sending message: {e.response['error']}")


if __name__ == "__main__":
    get_pur()
    get_users()

#     with open("./db/ctnt.json", "r") as f:
#         data = json.load(f)
#     for user in data:
#         if 0 < int(data[user]["PUR"]) < 90:
#             message_weekly_less = f"""

# Привет. Заметил, что у тебя PUR текущий месяц значительно меньше чем мы ожидаем (PUR - соотношение между прод временем в табличке Canvas Task & Time и времени записанном в метадате на работах).

# Данные:
# - Твой PUR - {data[user]["PUR"]}%
# - Ожидаемый PUR - 95%
# - Canvas Task & Time - {data[user]["Table time"]} мин
# - Метадата - {data[user]["metadata"]} мин

# Разница в {int(data[user]["Table time"]) - int(data[user]["metadata"])}
# Возможно у тебя есть работы в процессе в которых ты еще не заполнил(а) метадату? Если такие есть, можешь подсказать сколько минут ты на них потратил(а)?

# Автор бота: <@U05HCBAPKKM>. Отправь мне это сообщение с ответом :02_cheer:
# """
#             send_message(
#                 data[user]["ID"],
#                 data[user]["Name"],
#                 data[user]["PUR"],
#                 message_weekly_less,
#             )

#         if int(data[user]["PUR"]) > 120:
#             message_weekly_more = f"""

# Привет. Заметил, что у тебя PUR текущий месяц значительно больше чем мы ожидаем (PUR - соотношение между прод временем в табличке Canvas Task & Time и времени записанном в метадате на работах).

# Данные:
# - Твой PUR - {data[user]["PUR"]}%
# - Ожидаемый PUR - 95%
# - Canvas Task & Time - {data[user]["Table time"]} мин
# - Метадата - {data[user]["metadata"]} мин

# Разница в {int(data[user]["metadata"]) - int(data[user]["Table time"]) }

# Проверь заполнены ли у тебя все дни в текущем месяце в Canvas Task & Time 2.0.
# Возможно у тебя перенеслась отправка работ с прошлого месяца в текущий.

# Автор бота: <@U05HCBAPKKM>. Отправь мне это сообщение с ответом :02_cheer:
# """
#             send_message(
#                 data[user]["ID"],
#                 data[user]["Name"],
#                 data[user]["PUR"],
#                 message_weekly_more,
#             )
