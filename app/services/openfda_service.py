import httpx
from app.config import settings
import requests
from typing import TypedDict, List, Optional, Union

class OpenFDAInfo(TypedDict):
    application_number: List[str]
    brand_name: List[str]
    generic_name: List[str]
    manufacturer_name: List[str]
    product_ndc: List[str]
    product_type: List[str]
    route: List[str]
    substance_name: List[str]
    rxcui: List[str]
    spl_id: List[str]
    spl_set_id: List[str]
    package_ndc: List[str]
    is_original_packager: List[bool]
    upc: List[str]
    unii: List[str]

class MedicineResult(TypedDict):
    spl_product_data_elements: List[str]
    active_ingredient: List[str]
    purpose: List[str]
    indications_and_usage: List[str]
    warnings: List[str]
    do_not_use: List[str]
    ask_doctor: List[str]
    ask_doctor_or_pharmacist: List[str]
    stop_use: List[str]
    pregnancy_or_breast_feeding: List[str]
    keep_out_of_reach_of_children: List[str]
    dosage_and_administration: List[str]
    storage_and_handling: List[str]
    inactive_ingredient: List[str]
    set_id: str
    id: str
    effective_time: str
    version: str
    openfda: OpenFDAInfo

class OpenFDAService:
    def __init__(self):
        self.base_url = "https://api.fda.gov/drug"
        self.api_key = settings.OPENFDA_API_KEY

    def find_medicine_by_label(self, generic_name: str) -> Optional[MedicineResult]:
        """
        Finds a medicine by its generic name using the OpenFDA API.

        Args:
            generic_name (str): The generic name of the medicine to search for.

        Returns:
            Optional[MedicineResult]: A dictionary containing the medicine data, or None if not found.
        """
        base_url = "https://api.fda.gov/drug/label.json"
        params = {
            "search": f"openfda.generic_name:{generic_name}",
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            print(data)
            if data["meta"]["results"]["total"] > 0:
                return data["results"][0]
            else:
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching medicine data: {e}")
            return None