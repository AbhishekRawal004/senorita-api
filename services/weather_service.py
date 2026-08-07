import requests


class WeatherService:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url

    def get_weather(self, city):
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        response = requests.get(
            self.api_url,
            params=params,
            timeout=5
        )

        

        return response.json()