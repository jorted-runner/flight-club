import requests
import datetime as dt
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def configure():
    load_dotenv()

configure()

tequila_api = os.environ.get("tequila_api")


class DataManager:
    def __init__(self):
        self.SHEETY_TOKEN = os.environ.get("SHEETY_TOKEN")
        self.SHEETY_ENDPOINT = os.environ.get("sheety_price")
        tommorrow = dt.datetime.now() + dt.timedelta(days=1)
        six_month = dt.datetime.now() + dt.timedelta(days=180)
        self.tommorrow = tommorrow.strftime("%d/%m/%Y")
        self.six_month = six_month.strftime("%d/%m/%Y")

    def update_sheet_w_iata(self, data):
        endpoint = f"{self.SHEETY_ENDPOINT}/{data['id']}"
        sheet_input = {
            "price":
                data
        }
        response = requests.put(url=endpoint, json=sheet_input)
        response.raise_for_status()

    def get_emails(self):
        response = requests.get(url=os.environ.get("sheety_email"))
        data = response.json()["users"]
        return data
