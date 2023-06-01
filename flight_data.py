class FlightData:

    def get_lowest_price(self, data, highest_price):
        lowest = highest_price
        cheapest_flight = []
        for item in data:
            if item["price"] < lowest:
                lowest = item["price"]
                cheapest_flight = item
        return cheapest_flight

    def get_dates_of_flights(self, data):
        departure = data["route"][0]["local_departure"].split("T")

        return_date = data["route"][-1]["local_departure"].split("T")
        return departure[0], return_date[0]