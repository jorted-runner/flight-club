from twilio.rest import Client
import smtplib
from data_manager import DataManager
import os
from dotenv import load_dotenv

def configure():
    load_dotenv()

configure()

class NotificationManager:
    def __init__(self):
        self.my_email = os.environ.get("my_email")
        self.my_password = os.environ.get("my_password")
        self.data_manager = DataManager()

    def send_email(self, data, departure, return_date, buy_url, user_email):
        alert = f"Low price alert! Only ${data['price']:.2f} to fly from {data['cityFrom']}-{data['flyFrom']} to " \
                f"{data['cityTo']}-{data['flyTo']}, from {departure} to {return_date}"

        connection = smtplib.SMTP("smtp.gmail.com", port=587)
        connection.starttls()
        connection.login(user=self.my_email, password=self.my_password)
        connection.sendmail(to_addrs=user_email, from_addr=self.my_email, msg=f"Subject: Flight Club\n\n{alert}\n\n{buy_url}")
        connection.close()
