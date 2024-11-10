import httpx
from app.config import settings

class OpenFDAService:
    def __init__(self):
        self.base_url = "https://api.fda.gov/drug"
        self.api_key = settings.OPENFDA_API_KEY

    async def search_medicine(self, query: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/ndc.json",
                params={
                    "api_key": self.api_key,
                    "search": f"brand_name:{query}",
                    "limit": 1
                }
            )
            return response.json() 