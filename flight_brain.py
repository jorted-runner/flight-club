from data_manager import DataManager
from flight_search import FlightSearch
from flight_data import FlightData
from notification_manager import NotificationManager


data_manager = DataManager()
flight_search = FlightSearch()
notifications = NotificationManager()
sheet_data = data_manager.get_cities()

for item in sheet_data:
    if item["iataCode"] == "":
        sheet_data = flight_search.get_iata_codes(item)

    cheap_flights, PRICE = flight_search.search_cheap_flights(item)
    find_cheapest = FlightData()
    lowest = find_cheapest.get_lowest_price(cheap_flights, PRICE)

    if len(lowest) == 0:
        pass
    else:
        departure, return_date = find_cheapest.get_dates_of_flights(lowest)
        notifications.send_email(lowest, departure, return_date)
