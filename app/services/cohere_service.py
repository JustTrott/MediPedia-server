import cohere
from app.config import settings

class CohereService:
    def __init__(self):
        self.client = cohere.Client(settings.COHERE_API_KEY)
    
    async def analyze_sentiment(self, text: str) -> float:
        response = self.client.classify(
            model='sentiment',
            inputs=[text]
        )
        return float(response.classifications[0].confidence) 