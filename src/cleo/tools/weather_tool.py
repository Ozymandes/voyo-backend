"""
Weather Tool for CLEO
Real-time weather information for Egyptian cities
"""

import requests
from typing import Dict, Optional, Tuple
import os
import logging

logger = logging.getLogger(__name__)

class WeatherTool:
    """Get weather information for travel planning"""

    def __init__(self):
        """Initialize weather tool"""
        self.api_key = os.getenv("WEATHER_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5"

        if self.api_key:
            logger.info("Weather tool initialized with OpenWeatherMap API")
        else:
            logger.warning("WEATHER_API_KEY not found - weather tool disabled")

    def get_current_weather(self, city: str) -> Optional[Dict]:
        """
        Get current weather for city

        Args:
            city: City name in Egypt

        Returns:
            Weather dictionary or None
        """
        if not self.api_key:
            return {"error": "Weather API not configured"}

        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": f"{city},EG",
                "appid": self.api_key,
                "units": "metric"
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            return {
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "conditions": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "icon": data["weather"][0]["icon"]
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in weather tool: {e}")
            return {"error": str(e)}

    def assess_suitability(
        self,
        city: str,
        activity_type: str = "general"
    ) -> Tuple[bool, str]:
        """
        Assess if weather is suitable for activity

        Args:
            city: City name
            activity_type: Type of activity (general, outdoor, sightseeing)

        Returns:
            Tuple of (is_suitable, reason)
        """
        weather = self.get_current_weather(city)

        if "error" in weather:
            return True, "Weather information unavailable"

        temp = weather["temperature"]
        conditions = weather["conditions"].lower()
        wind = weather["wind_speed"]

        # Hot weather
        if temp > 35:
            if activity_type == "outdoor":
                return False, f"It's quite hot ({temp}°C). Early morning or late afternoon would be better for outdoor activities."
            else:
                return True, f"It's hot ({temp}°C). Indoor attractions with AC would be comfortable!"

        # Rain
        if "rain" in conditions or "drizzle" in conditions:
            if activity_type == "outdoor":
                return False, "It's raining. Indoor attractions like museums would be better today."
            else:
                return True, f"Some rain ({conditions}), but indoor activities are perfect!"

        # Wind (potential sandstorms)
        if wind > 10:
            return False, f"It's quite windy ({wind} m/s). Might not be ideal for outdoor sites today."

        # Good weather
        if 20 <= temp <= 30 and "clear" in conditions:
            return True, f"Perfect weather! {temp}°C and {conditions}. Great for exploring!"

        return True, f"Weather is okay. {temp}°C and {conditions}."

    def get_forecast(self, city: str, days: int = 3) -> list:
        """
        Get weather forecast

        Args:
            city: City name
            days: Number of days to forecast

        Returns:
            List of forecast dictionaries
        """
        if not self.api_key:
            return [{"error": "Weather API not configured"}]

        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": f"{city},EG",
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (every 3 hours)
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            # Extract daily forecasts (noon)
            forecasts = []
            for item in data["list"]:
                if "12:00:00" in item["dt_txt"] or "15::00:00" in item["dt_txt"]:
                    forecasts.append({
                        "date": item["dt_txt"].split()[0],
                        "temp": item["main"]["temp"],
                        "conditions": item["weather"][0]["description"],
                        "humidity": item["main"]["humidity"]
                    })

            return forecasts[:days]

        except Exception as e:
            logger.error(f"Error getting forecast: {e}")
            return [{"error": str(e)}]
