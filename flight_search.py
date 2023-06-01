import requests
from data_manager import DataManager
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy


def configure():
    load_dotenv()

configure()


class FlightSearch:
    def __init__(self):
        self.TEQUILA_API = os.environ.get("tequila_api")
        self.location_search = "/locations/query"
        self.price_search = "/v2/search"
        self.TEQUILA_ENDPOINT = os.environ.get("tequila_endpoint")
        self.HEADER = {
            "accept": "application/json",
            "apikey": self.TEQUILA_API
        }
        self.data_manager = DataManager()

    def get_iata_codes(self, city_data):
        search_params = {
            "term": city_data,
            "locale": "en-US",
            "location_types": "airport",
            "limit": 10,
            "active_only": True
        }

        endpoint = f"{self.TEQUILA_ENDPOINT}{self.location_search}"
        response = requests.get(url=endpoint, params=search_params, headers=self.HEADER)
        response.raise_for_status()

        iata_code = response.json()["locations"][0]["code"]

        return iata_code

    def search_cheap_flights(self, item):
        endpoint = f"{self.TEQUILA_ENDPOINT}{self.price_search}"
        FLY_FROM = f"airport:{item.fly_from_iata}"
        FLY_TO = f"airport:{item.dest_iata_code}"
        PRICE = int(item.max_price)
        min_nights = int(item.min_nights)
        max_nights = int(item.max_nights)
        max_stopovers = int(item.max_stopovers)
        len_stopovers = f"{item.max_leng_stopovers}:00"
        search_terms = {
            "fly_from": FLY_FROM,
            "fly_to": FLY_TO,
            "date_from": self.data_manager.tommorrow,
            "date_to": self.data_manager.six_month,
            "nights_in_dst_from": min_nights,
            "nights_in_dst_to": max_nights,
            "flight_type": "round",
            "curr": "USD",
            "locale": "us",
            "price_from": 10,
            "price_to": PRICE,
            "max_stopovers": max_stopovers,
            "stopover_to": len_stopovers
        }

        response = requests.get(endpoint, params=search_terms, headers=self.HEADER)
        response.raise_for_status()
        flight_search_response = response.json()["data"]
        return flight_search_response, PRICE
