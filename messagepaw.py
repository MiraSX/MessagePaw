import slack
import os
import json
import re
import logging
from slack.errors import SlackApiError
from dotenv import load_dotenv
from sheetpaw import get_pur

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)


client = slack.WebClient(token=os.getenv("BOT_TOKEN"))

users = client.users_list()["members"]

data = {}

print(users)


def get_users():
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

    with open("./db/ctnt.json", "w") as f:
        json.dump(data_ctnt, f, indent=4, separators=(",", ": "))


def send_message(user_id, message):
    try:
        response = client.chat_postMessage(channel=user_id, text=message)
        logging.debug(f"Message sent to {user_id}: {response.get('ok')}")
    except SlackApiError as e:
        logging.debug(f"Error sending message: {e.response['error']}")


if __name__ == "__main__":
    # get_pur()
    # get_users()

    with open("./db/ctnt.json", "r") as f:
        data = json.load(f)
    for user in data:
        if 0 < int(data[user]["PUR"]) < 90:
            #             message_month = f"""

            #     Привет!

            #     Заметил, что твой PUR за прошлый месяц (PUR - соотношение между прод временем в табличке Canvas Task & Time и времени записанном в метадате на работах) немного ниже значения, что мы ожидаем.

            #     Данные:

            #     - Твой PUR - {data[user]["pur"]}%
            #     - Ожидаемый PUR - 95%

            #     Пожалуйста обрати внимание на этот показатель в текущем месяце. Если значение будет слишком низким, мы вынуждены будем оплачивать ЗП лишь по Active time с Insightful.

            #     Автор бота: <@U05HCBAPKKM> (Отпишитесь мне в личку пришло ли вам сообщение :slightly_smiling_face:) Если возникнут вопросы, пиши)
            #     """
            message_weekly = f"""

Привет. Заметил, что у тебя PUR текущий месяц значительно меньше чем мы ожидаем (PUR - соотношение между прод временем в табличке Canvas Task & Time и времени записанном в метадате на работах).

Данные:
- Твой PUR - {data[user]["PUR"]}%
- Ожидаемый PUR - 90%
- Canvas Task & Time - {data[user]["Table time"]} мин
- Метадата - {data[user]["metadata"]} мин

Разница в {int(data[user]["Table time"]) - int(data[user]["metadata"])} минут показывает, что ты на работе в которых еще не заполнил(а) метадату.
Возможно у тебя есть работы в процессе в которых ты еще не заполнил(а) метадату? Если такие есть, можешь подсказать сколько минут ты на них потратил(а)?

Автор бота: <@U05HCBAPKKM>. Отправь мне это сообщение с ответом :02_cheer:
"""
            #             send_message(data[user]["ID"], message_weekly)

            # # Для теста
            send_message(data[user]["ID"], message_weekly)
