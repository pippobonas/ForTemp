import asyncio
from .AsyncHttpClient import AsyncHttpClient

class OpenWeatherCurrentWeather(AsyncHttpClient):
    """Client for fetching current weather data from OpenWeather."""
    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url)
        if api_key is not None:
            self.api_key = api_key
        else:
            raise ValueError("API key must be provided.")
        
    def __str__(self) -> str:
        return f"OpenWeatherCurrentWeatherURL: {self.base_url}"

    async def get_current_weather(self, latitude: float, longitude: float, retries: int = 3, **kwargs):
        """Fetch current weather data."""
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key
        }
        return await self.get(params=params, retries=retries)

class OpenWeatherGeocoding(AsyncHttpClient):
    """Client for geolocation-related data from OpenWeather."""
    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url)
        self.api_key = api_key
        
    def __str__(self) -> str:
        return f"OpenWeatherGeocoding: {self.base_url}"

    async def get_geolocation(self, city: str, retries: int = 3) -> list:
        """Fetch geolocation data for a specific city."""
        params = {"q": city, "appid": self.api_key}
        return await self.get(params=params, retries=retries)