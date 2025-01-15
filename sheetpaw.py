import os
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
CTnT_SPREADSHEET_ID = os.getenv("CTnT_SPREADSHEET_ID")
CTnT_RANGE_NAME = os.getenv("CTnT_RANGE_NAME")
SK_SPREADSHEET_ID = os.getenv("SK_SPREADSHEET_ID")
SK_RANGE_NAME = os.getenv("SK_RANGE_NAME")

data_ctnt = {}
data_sk = {}

data = {}


def get_pur():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("./db/token.json"):
        creds = Credentials.from_authorized_user_file("./db/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "./db/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("./db/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=CTnT_SPREADSHEET_ID, range=CTnT_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        for row in values:
            if len(row) > 6:
                data_ctnt[row[0]] = {
                    "metadata": row[2],
                    "Table time": row[-2],
                    "PUR": row[-1].replace("%", ""),
                }

        result = (
            sheet.values()
            .get(spreadsheetId=SK_SPREADSHEET_ID, range=SK_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        for row in values:
            data_sk[row[-1]] = row[-0]

    except HttpError as err:
        print(err)

    for i in data_ctnt:
        if i in data_sk:
            data_ctnt[i]["Name"] = data_sk[i]

    with open("./db/ctnt.json", "w") as f:
        json.dump(data_ctnt, f, indent=4, separators=(",", ": "))


if __name__ == "__main__":
    get_pur()
