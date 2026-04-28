import httpx
from typing import Dict, Any, Optional
from config import settings
import json
import logging

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)
    
    async def chat_completion(
        self, 
        model: str = "llama3-70b-8192",
        messages: list,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """Send chat completion request to Groq"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            logger.info(f"Groq API success: {len(content)} chars")
            return content
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Groq HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return None
        finally:
            await self.client.aclose()
    
    async def extract_invoice_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract structured invoice data using Llama 3 70B"""
        prompt = f"""
You are an expert invoice parser. Extract ALL invoice data from this text.

RETURN ONLY VALID JSON with this EXACT structure. No explanations.

{{
  "invoice_number": "INV-123 or null",
  "date": "YYYY-MM-DD or null", 
  "vendor": "Company name or null",
  "subtotal": 123.45,
  "tax": 12.34,
  "total": 135.79,
  "currency": "USD",
  "category": "Office Supplies|Travel|Marketing|Utilities|Other",
  "items": [
    {{
      "description": "Item name",
      "quantity": 2,
      "unit_price": 10.99,
      "total_price": 21.98
    }}
  ],
  "confidence": 0.95
}}

INVOICE TEXT:
{text[:4000]}

JSON ONLY:
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages=messages, temperature=0.1)
        
        if response:
            try:
                # Extract JSON from response
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error("Failed to parse Groq JSON response")
                return None
        
        return None

# Global instance
groq = GroqService()
