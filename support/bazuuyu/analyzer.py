import json
import google.generativeai as genai

from support.config import GEMINI_API_KEY, GEMINI_MODEL


# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(GEMINI_MODEL)


def analyze_trend(trend: dict) -> dict:
    """
    Analyze a detected trend from the perspective of
    toys, plush, collectibles, and Bazuuyu.
    """

    prompt = f"""
You are a trend intelligence analyst working for Bazuuyu,
a plush and collectible toy brand.

Analyze the following detected social-media trend.

TREND:
{json.dumps(trend, ensure_ascii=False, indent=2)}

Your job is NOT to invent facts.

Evaluate whether this trend could be relevant to:
- toys
- plush toys
- collectibles
- character merchandise
- social-media content
- Bazuuyu products

Return ONLY valid JSON with exactly these fields:

{{
  "trend": "",
  "trend_strength": 0,
  "toy_relevance": 0,
  "plush_relevance": 0,
  "collectible_relevance": 0,
  "bazuuyu_relevance": 0,
  "audience": [],
  "themes": [],
  "visual_styles": [],
  "content_opportunities": [],
  "product_opportunities": [],
  "reasoning": ""
}}

Scoring:
- trend_strength: 0-100
- toy_relevance: 0-100
- plush_relevance: 0-100
- collectible_relevance: 0-100
- bazuuyu_relevance: 0-100

Important:
- Do not assume that every trend is relevant to Bazuuyu.
- If relevance is low, give a low score.
- Do not invent sales data.
- Do not claim that something is popular unless the supplied trend evidence supports it.
- Separate observed evidence from your interpretation.
- Keep recommendations practical for a plush/collectible toy company.
"""

    try:
        response = model.generate_content(prompt)

        text = response.text.strip()

        # Remove markdown code fences if Gemini adds them
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        result = json.loads(text)

        return result

    except Exception as e:
        return {
            "error": str(e),
            "trend": trend.get("title", ""),
        }
