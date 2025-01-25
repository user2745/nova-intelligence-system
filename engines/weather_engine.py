# context_engines/weather_engine.py
import os
import requests

class WeatherEngine:
    """
    Gathers and processes real-time weather context for the Nova system.
    """

    def __init__(self):
        self.name = "WeatherEngine"
        # It's best to keep your API key in an environment variable:
        # export OPENWEATHERMAP_API_KEY="your_api_key"
        self.api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "")

    def gather_context(self, location="Boone"):
        """
        Fetches current weather data from an external API.
        """
        if not self.api_key:
            print("No API key found. Please set OPENWEATHERMAP_API_KEY in your environment.")
            return {}

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={location}&appid={self.api_key}"
        )
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Convert temperature from Kelvin to Celsius, if desired.
            temperature_c = data["main"]["temp"] - 273.15
            
            # Build a dictionary of relevant weather data.
            weather_context = {
                "location": location,
                "temperature_c": round(temperature_c, 2),
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
            }
            return weather_context

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred while fetching weather: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error occurred while fetching weather data: {req_err}")
        except KeyError as key_err:
            print(f"Unexpected data format in API response: Missing key {key_err}")

        return {}

    def run(self, location="London"):
        """
        Runs the engine, returning or optionally logging the weather data.
        """
        weather_data = self.gather_context(location)
        # Here you could store, log, or further process the weather_data
        if weather_data:
            print(f"Weather data for {location}: {weather_data}")
        return weather_data
