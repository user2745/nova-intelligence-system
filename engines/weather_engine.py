# context_engines/weather_engine.py
class WeatherEngine:
    def __init__(self):
        self.name = "WeatherEngine"

    def gather_context(self):
        # Simulate a weather API
        return {"weather": "Sunny", "temperature": "25°C"}

    def run(self):
        return "WeatherEngine is running!"
