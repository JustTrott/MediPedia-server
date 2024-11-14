import httpx
from app.config import settings
import requests

class OpenFDAService:
    def __init__(self):
        self.base_url = "https://api.fda.gov/drug"
        self.api_key = settings.OPENFDA_API_KEY

    def find_medicine_by_label(self, generic_name):
        """
        Finds a medicine by its generic name using the OpenFDA API.

        Args:
            generic_name (str): The generic name of the medicine to search for.

        Returns:
            dict: A dictionary containing the medicine data, or None if not found.
        """
        base_url = "https://api.fda.gov/drug/label.json"
        params = {
            "search": f"openfda.generic_name:{generic_name}",
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data["meta"]["total"] > 0:
                return data["results"][0]
            else:
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching medicine data: {e}")
            return None