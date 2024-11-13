import cohere
import json
from app.config import settings

class CohereService:
    def __init__(self):
        self.client = cohere.ClientV2(settings.COHERE_API_KEY)
    
    async def extract_label(self, text: str) -> str:
        """
        Extract generic drug name from unstructured text using Cohere's generate endpoint.
        
        Args:
            text (str): Unstructured text containing drug information
            
        Returns:
            str: Generic drug name
        """
        prompt = f"""Extract the generic drug name from the following text. 
Return only the generic name without any additional text or formatting.

Examples:
--
Text: "Tylenol (acetaminophen) 500mg tablets"
acetaminophen
--
Text: "Advil tablets containing ibuprofen 200mg"
ibuprofen
--
Text: "Amoxicillin 500mg antibiotic capsules"
amoxicillin
--
Text: {text}
"""

        response = await self.client.generate(
            model="command",
            prompt=prompt,
            max_tokens=20,
            temperature=0.0,  # Use low temperature for consistent extraction
            k=0,
            stop_sequences=["--"],
        )

        # Get the generated text and clean it
        extracted_name = response.generations[0].text.strip().lower()
        
        # Remove any extra whitespace or newlines
        extracted_name = " ".join(extracted_name.split())
        
        return extracted_name

    async def filter_by_profile(self, medicine_data: str, profile_data: str) -> dict:
        """
        Analyze if a medicine is safe for a patient based on their profile.
        
        Args:
            medicine_data (str): JSON string containing medicine information
            profile_data (str): JSON string containing patient profile information
            
        Returns:
            dict: Contains 'can_take' (bool) and 'warning' (str or None)
        """
        prompt = f"""You are a medical safety assistant. Analyze if the medicine is safe for the patient based on their profile.
Return a JSON object with two fields:
- can_take: boolean indicating if the medicine is safe
- warning: string explaining any issues, or null if there are no issues

Consider:
- Patient allergies
- Medical conditions
- Current medications (potential interactions)
- Age-related restrictions
- Any other relevant safety concerns

Examples:
--
Medicine: {{"name": "Aspirin", "description": "Blood thinner, pain reliever"}}
Profile: {{"allergies": "aspirin, penicillin", "conditions": "none", "age": 45}}
{{"can_take": false, "warning": "Patient has aspirin allergy - DO NOT TAKE"}}
--
Medicine: {{"name": "Ibuprofen", "description": "NSAID pain reliever"}}
Profile: {{"allergies": "none", "conditions": "peptic ulcer", "age": 35}}
{{"can_take": false, "warning": "NSAIDs can worsen peptic ulcers - avoid use"}}
--
Medicine: {{"name": "Acetaminophen", "description": "Pain reliever and fever reducer"}}
Profile: {{"allergies": "none", "conditions": "none", "age": 30}}
{{"can_take": true, "warning": null}}
--
Medicine: {medicine_data}
Profile: {profile_data}
"""

        try:
            response = await self.client.generate(
                model="command",
                prompt=prompt,
                max_tokens=200,
                temperature=0.0,
                k=0,
                stop_sequences=["--"],
            )

            # Get the generated text and clean it
            result_text = response.generations[0].text.strip()
            
            try:
                # Parse the JSON response
                result = json.loads(result_text)
                
                # Convert string 'true'/'false' to boolean if needed
                can_take = result.get('can_take')
                if isinstance(can_take, str):
                    can_take = can_take.lower() == 'true'
                    result['can_take'] = can_take
                
                # Ensure the response has the required fields
                if not isinstance(result.get('can_take'), bool):
                    return {
                        "can_take": False,
                        "warning": "Error analyzing medicine safety - invalid response format"
                    }
                
                if result.get('warning') is not None and not isinstance(result.get('warning'), str):
                    result['warning'] = str(result.get('warning'))
                    
                return result
                
            except (json.JSONDecodeError, KeyError, ValueError):
                return {
                    "can_take": False,
                    "warning": "Error analyzing medicine safety - please consult a healthcare provider"
                }
                
        except Exception as e:
            return {
                "can_take": False,
                "warning": f"Error analyzing medicine safety: {str(e)}"
            }
        