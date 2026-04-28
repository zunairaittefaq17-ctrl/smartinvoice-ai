import groq
from config import settings

client = groq.Groq(api_key=settings.GROQ_API_KEY)

INVOICE_EXTRACTION_PROMPT = """
You are a financial AI assistant. Extract structured invoice data from the following text.

Return ONLY valid JSON in this exact format:
{{
  "invoice_number": "INV-123",
  "date": "2024-01-15",
  "vendor": "ABC Company",
  "items": [
    {{
      "description": "Product 1",
      "quantity": 2,
      "unit_price": 10.99,
      "total_price": 21.98
    }}
  ],
  "subtotal": 21.98,
  "tax": 2.20,
  "total": 24.18,
  "currency": "USD",
  "category": "Office Supplies"
}}

Text to analyze:
{raw_text}

Return ONLY JSON, no other text.
"""

INSIGHTS_PROMPT = """
Analyze these expenses and provide insights:

Total expenses: ${total}
Monthly expenses: ${monthly}
Top category: {top_category}
Top vendor: {top_vendor}

Provide:
1. Expense summary
2. Savings suggestions  
3. Potential fraud warnings
4. Spending behavior analysis

Return JSON:
{{
  "summary": "...",
  "savings_tips": "...",
  "warnings": ["warning1", "warning2"],
  "behavior_analysis": "..."
}}
"""

async def extract_invoice_data(raw_text: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": INVOICE_EXTRACTION_PROMPT.format(raw_text=raw_text)}],
            temperature=0.1,
            max_tokens=2000
        )
        return eval(response.choices[0].message.content)  # Safe eval for JSON
    except Exception as e:
        print(f"Groq extraction error: {e}")
        return {}

async def generate_insights(analytics_data: dict) -> dict:
    try:
        prompt = INSIGHTS_PROMPT.format(
            total=analytics_data.get('total_expenses', 0),
            monthly=analytics_data.get('monthly_expenses', 0),
            top_category=analytics_data.get('top_category', 'N/A'),
            top_vendor=analytics_data.get('top_vendor', 'N/A')
        )
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return eval(response.choices[0].message.content)
    except:
        return {
            "summary": "Unable to generate insights",
            "savings_tips": "Review your spending",
            "warnings": [],
            "behavior_analysis": "Monitor expenses closely"
        }
