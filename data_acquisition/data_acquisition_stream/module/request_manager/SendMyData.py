from module.request_manager.AsyncHttpClient import AsyncHttpClient as AsyncHttpClient
from module.utils import filter_data as fil

class SendMyData(AsyncHttpClient):
    """Client for sending data to Logstash."""
    def __init__(self, base_url: str):
        super().__init__(base_url)

    async def send_log(self, data: dict, retries: int = 5):
        """Send logs to Logstash."""
        res=await self.post(data, retries)
        return res
    
    async def send_normalized(self,data, **kwargs):
        """Send normalized data to a Logstash server."""
        data = fil.extract_data(data)
        data = fil.normalize_data(data)
        if kwargs.get("city"):
            data["city"] = kwargs.get("city")
        return await self.send_log(data)
        