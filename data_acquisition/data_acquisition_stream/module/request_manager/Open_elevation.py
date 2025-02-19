from .AsyncHttpClient import AsyncHttpClient

class Open_elevation(AsyncHttpClient):
    """Client for fetching elevation data from Open-elevation."""
    def __init__(self, base_url: str):
        super().__init__(base_url)
    
    def __str__(self) -> str:
        return f"Open-elevation client at {self.base_url}"
    
    async def get_elevation(self, lat: float, lon: float, retries: int = 3):
        """Fetch elevation data for a specific latitude and longitude."""
        params = {"locations": f"{lat},{lon}"}
        data = await self.get(params=params, retries=retries)
        return data["results"][0]["elevation"]
