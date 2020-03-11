import requests
import json
from datetime import datetime


class WebDataRetriever():

    def __init__(self):
        self.weatherurl = 'http://api.openweathermap.org/data/2.5/forecast?q=Mumbai&cnt=5&appid=apikey'

    def get_estimated_yield(self):
        cloud_average = self.get_weather_data() / 100
        month = datetime.now().month

        sun_hours = 13 - (13*cloud_average)
        m = 1.01278225014726
        c = 1.41708226978205
        daily_yield = m*sun_hours + c

        if month < 4 or month > 9:
            return daily_yield
        elif 3 <= month < 6:
            return daily_yield + 1
        else:
            return daily_yield + 2

    def get_weather_data(self):
        response = requests.get(self.weatherurl)
        weather_data = json.loads(response.text)['list']
        cloud_average = self.calculate_average_clouds(weather_data)
        return cloud_average

    def calculate_average_clouds(self, data):
        cloud_percentage_daily_average = counter = 0

        for hourly_data in data:
            timestamp = hourly_data['dt']
            count_until_time = WebDataRetriever.convert_timestamp_to_hour(timestamp)
            if count_until_time < 20:
                current_cloud_percentage = hourly_data['clouds']['all']
                cloud_percentage_daily_average += current_cloud_percentage
                counter += 1
            elif counter == 0:
                current_cloud_percentage = hourly_data['clouds']['all']
                cloud_percentage_daily_average += current_cloud_percentage
                counter += 1
            else:
                break
        return cloud_percentage_daily_average / counter

    @staticmethod
    def convert_timestamp_to_hour(timestamp):
        return datetime.fromtimestamp(timestamp).hour - 1



dataretriever = WebDataRetriever()
estimated_daily_yield = round(dataretriever.get_estimated_yield(), 2)
print(estimated_daily_yield)