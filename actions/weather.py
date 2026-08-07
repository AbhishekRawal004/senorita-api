from services.weather_service import WeatherService
import re


class WeatherAction:

    def __init__(self, api_key, api_url):
        self.weather_service = WeatherService(api_key, api_url)

    def execute(self, city, speak):
        try:
            city = re.sub(r"[^\w\s-]", "", city).strip()
            data = self.weather_service.get_weather(city)

            if data.get("cod") != 200:
                speak(
                    f"Sorry, I couldn't find the weather for {city}."
                )
                return False

            weather = data["weather"][0]["description"]
            temperature = int(data["main"]["temp"])

            speak(
                f"The weather in {city.title()} is currently {weather}, "
                f"with a temperature of {temperature} degrees Celsius."
            )

            return True

        except Exception as e:
            print(f"Weather Error: {e}")
            speak("I'm having trouble connecting to the weather service right now.")
            return False