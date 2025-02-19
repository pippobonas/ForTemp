import asyncio
import aiohttp
from module.utils.my_log import stdo, stde, stdw

class AsyncHttpClient:
    """Class to manage asynchronous HTTP requests with GET and POST methods."""

    def __init__(self, base_url: str, **kwargs):
        """
        Initialize the HTTP client.

        Args:
            base_url (str): Base URL for API requests.
        """
        self.base_url = base_url
        self.session = None
    
    def __str__(self) -> str:
        return f"AsyncHttpClient(base_url={self.base_url})"

    async def __aenter__(self):
        """Creates and manages the HTTP session context."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Closes the HTTP session."""
        if self.session:
            await self.session.close()

    async def get(self, params: dict = None, retries: int = 3, endpoint="", **kwargs) -> dict:
        """
        Perform a GET request with retry support.

        Args:
            endpoint (str): API endpoint (e.g., '/path').
            params (dict, optional): Query string parameters.
            retries (int): Number of attempts in case of failure.

        Returns:
            dict: JSON response from the server.
        """
        url = f"{self.base_url}{endpoint}"
        for attempt in range(1, retries + 1):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 400:  # bad request without retrying
                        stdw(f"[GET][REQ]->Bad Request (HTTP 400) on attempt {attempt}")
                        return
                    response.raise_for_status()  # exception for HTTP errors
                    stdo(f"[GET][REQ]-> successful: {url}")
                    # Check the response content type
                    if response.content_type == 'application/json':
                        res = await response.json()  # Return the successful response
                    elif response.content_type == 'text/plain' or response.content_type == 'text/html':
                        res = await response.text()
                    else:
                        x = (f"Unsupported content type: {response.content_type}")
                        stde(f"[POST][RES]->{x}")
                    stdo(f"[POST][RES]->{response.status}{response.content_type}")
                    return res
                
            except aiohttp.ClientError as e:
                stde(f"[GET][REQ]-> failed (attempt {attempt}/{retries}): {e}")
                if attempt == retries:
                    raise  # Raise exception if all attempts fail
                
                await asyncio.sleep(10)

    async def post(self, data: dict =None, retries: int = 3, endpoint: str = "" , **kwargs) -> dict:
        """
        Perform a POST request with retry support.

        Args:
            endpoint (str): API endpoint (e.g., '/path').
            data (dict): Data to send in the request body.
            retries (int): Number of attempts in case of failure.

        Returns:
            dict: JSON response from the server if successful.
        """
        url = f"{self.base_url}{endpoint}"
        for attempt in range(1, retries + 1):
            try:
                async with self.session.post(url, json=data) as response:
                    if response.status == 400:  # Bad request without retrying
                        stdw(f"[POST][REQ]->Bad Request (HTTP 400) on attempt {attempt}")
                        return 
                    response.raise_for_status()  # Raise exception http errors
                    stdo(f"[POST][REQ]-> successful: {url}")
                    # Check the response content type
                    if response.content_type == 'application/json':
                        res = await response.json()  # Return the successful response
                    elif response.content_type == 'text/plain' or response.content_type == 'text/html':
                        res = await response.text()
                    else:
                        x = (f"Unsupported content type: {response.content_type}")
                        stde(f"[POST][RES]->{x}")
                    stdo(f"[POST][RES]->{response.status}{response.content_type}")
                    return res
                    
            except aiohttp.ClientError as e:
                stde(f"[POST][REQ]-> failed (attempt {attempt}/{retries}): {e}")
                if attempt == retries:
                    raise  # Raise exception if all attempts fail
                await asyncio.sleep(10)  # Delay between retries
