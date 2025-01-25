# modules/data_collector.py
import requests

class DataCollector:
    @staticmethod
    def fetch_crypto_data():
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url).json()
        return {
            "total_market_cap": response["data"]["total_market_cap"]["usd"],
            "total_volume": response["data"]["total_volume"]["usd"],
            "btc_dominance": response["data"]["market_cap_percentage"]["btc"]
        }

    @staticmethod
    def fetch_macro_data():
        # Example: Replace with Trading Economics API or similar
        return {
            "inflation_rate": "5.4%",
            "interest_rate": "4.5%",
            "gdp_growth": "2.3%"
        }
    
    @staticmethod
    def fetch_weather_data():
        # Example: Replace with OpenWeather API or similar
        return {
            "temperature": "22°C",
            "humidity": "55%",
            "weather": "Partly cloudy"
        }
    
    @staticmethod
    def fetch_news_data():
        # Example: Replace with News API or similar
        return {
            "headlines": [
                "News headline 1",
                "News headline 2",
                "News headline 3"
            ]
        }

    @staticmethod
    def fetch_social_data():
        # Example: Replace with social media API
        return {
            "trending_topics": [
                "Topic 1",
                "Topic 2",
                "Topic 3"
            ],
            "market_sentiment": [],
        }   
