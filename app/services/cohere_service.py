import cohere
import json
from app.config import settings

class CohereService:
    def __init__(self):
        self.client = cohere.ClientV2(settings.COHERE_API_KEY)
    
    def extract_label(self, text: str) -> str:
        """
        Extract generic drug name from unstructured text using Cohere's generate endpoint.
        
        Args:
            text (str): Unstructured text containing drug information
            
        Returns:
            str: Generic drug name
        """
        messages = [
            {
                "role": "system",
                "content": """You are a pharmaceutical expert. Extract the generic drug name (active ingredient) from the given text.

Rules:
- Convert brand names to their generic equivalent (e.g., Tylenol → acetaminophen)
- Return ONLY the generic name in lowercase, nothing else
- Use international generic names when possible (e.g., paracetamol → acetaminophen)
- If multiple drugs are mentioned, return only the primary active ingredient

Examples:
Input: "I have some Tylenol for my headache"
Output: acetaminophen

Input: "Taking 500mg paracetamol tablets"
Output: acetaminophen

Input: "Advil liquid gels 200mg"
Output: ibuprofen

Input: "My doctor prescribed Lipitor 40mg"
Output: atorvastatin"""
            },
            {
                "role": "user",
                "content": f"Text: {text}"
            }
        ]

        response = self.client.chat(
            model="command-r-plus",
            messages=messages,
            temperature=0.0,  # Use low temperature for consistent extraction
        )

        # Get the generated text and clean it
        extracted_name = response.message.content[0].text.strip().lower()
        
        # Remove any extra whitespace or newlines
        extracted_name = " ".join(extracted_name.split())
        
        return extracted_name

    def filter_by_profile(self, medicine_data: str, profile_data: str) -> dict:
        """
        Analyze if a medicine is safe for a patient based on their profile.
        
        Args:
            medicine_data (str): JSON string containing medicine information
            profile_data (str): JSON string containing patient profile information
            
        Returns:
            dict: Contains 'can_take' (bool) and 'warning' (str or None)
        """
        messages = [
            {
                "role": "system",
                "content": """You are a medical safety assistant. Analyze if the medicine is safe for the patient based on their profile. Make a decision that the medicine is unsafe only if any allergies or conditions of the user match the warnings of the medicine. Do it by taking an allergy of the user and searching for it in the information of the medicine. Only output it as a warning, if you find it.
Return a JSON object with two fields:
- can_take: boolean indicating if the medicine is safe
- warning: string explaining any issues, or null if there are no issues

Consider:
- if allergies and conditions say positive things like "none", "healthy" and deny having anything, output it as safe
- be more biased to not warn, rather than warn. make a warning after you make sure the warning is actually connected to an allergy or condition of the user
- Patient allergies: only create a warning when the side effects of the medicine exactly match the allergies of the user. Do not make up any allergies or do not assume anything more than what you are given.
- if the entries to allergies and conditions is nothing, the answer is most likely safe
- if the ingredient you warn about is not in the user's profile, do not warn about it
- Medical conditions
- Current medications (potential interactions)
- Age-related restrictions
- Any other relevant safety concerns, however do not assume any concern that is not mentioned in the medical data of the user
- if the person has not specified that they are pregnant, do not put a warning on that

Examples:
--
Medicine: {"name": "Aspirin", "description": "Blood thinner, pain reliever"}
Profile: {"allergies": "aspirin, penicillin", "conditions": "none", "age": 45}
{"can_take": false, "warning": "Patient has aspirin allergy - DO NOT TAKE"}
--
Medicine: {"name": "Ibuprofen", "description": "NSAID pain reliever"}
Profile: {"allergies": "none", "conditions": "peptic ulcer", "age": 35}
{"can_take": false, "warning": "NSAIDs can worsen peptic ulcers - avoid use"}
--
Medicine: {"name": "Acetaminophen", "description": "Pain reliever and fever reducer"}
Profile: {"allergies": "none", "conditions": "none", "age": 30}
{"can_take": true, "warning": null}response_format="json_object"
--"""
            },
            {
                "role": "user",
                "content": f"Medicine: {medicine_data}\nProfile: {profile_data}"
            }
        ]

        try:
            response = self.client.chat(
                model="command-r-plus",
                messages=messages,
                temperature=0.0,
                response_format={"type": "json_object"}
            )

            # Get the generated text and clean it
            result_text = response.message.content[0].text.strip()
            
            try:
                # Parse the JSON response
                print(result_text)
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
                
            except json.JSONDecodeError:
                return {
                    "can_take": False,
                    "warning": "Error analyzing medicine safety - please consult a healthcare provider"
                }
                
        except Exception as e:
            return {
                "can_take": False,
                "warning": f"Error analyzing medicine safety: {str(e)}"
            }
        