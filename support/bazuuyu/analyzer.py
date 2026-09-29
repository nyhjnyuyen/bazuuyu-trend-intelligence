# ============================================================
# BAZUUYU TREND ANALYZER
# ============================================================
#
# Purpose:
# Analyze trends detected by Trend-Finder and determine
# whether they may be relevant to Bazuuyu.
#
# ============================================================


# ------------------------------------------------------------
# 1. IMPORT LIBRARIES
# ------------------------------------------------------------

import json
import time

# Google Gemini API
from google import genai

# Bazuuyu Gemini configuration
from support.config import GEMINI_API_KEY, GEMINI_MODEL


# ------------------------------------------------------------
# 2. CONFIGURE GEMINI
# ------------------------------------------------------------
client = genai.Client(api_key=GEMINI_API_KEY)

# ------------------------------------------------------------
# 3. ANALYZE ONE TREND
# ------------------------------------------------------------

def analyze_trend(trend: dict) -> dict:
    """
    Analyze one detected trend from the perspective of Bazuuyu.

    Input:
        trend (dict)
            Trend information from Trend-Finder.

    Output:
        dict
            Gemini's structured analysis.
    """

    # --------------------------------------------------------
    # 4. CREATE THE AI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are a trend intelligence analyst working for Bazuuyu,
a plush and collectible toy company.

Analyze the following trend detected from social-media data.

TREND DATA:
{json.dumps(trend, ensure_ascii=False, indent=2)}

IMPORTANT:
The supplied trend data is the evidence.

Do NOT invent:
- sales numbers
- market size
- audience size
- growth percentages
- product performance
- demographic facts
- popularity claims

If the evidence does not support a conclusion, say so.

Analyze the trend for:

1. Toys
2. Plush toys
3. Collectibles
4. Character merchandise
5. Social-media content
6. Bazuuyu products

Identify:

- potential audience
- recurring themes
- visual characteristics
- content opportunities
- product opportunities
- Bazuuyu opportunities
- risks

Do not assume every trend is relevant to Bazuuyu.

A trend can have:
- high social momentum but low toy relevance
- high toy relevance but low Bazuuyu relevance
- high content potential but low product potential

Return ONLY valid JSON.

Use exactly these fields:

{{
  "trend": "",
  "evidence_summary": "",
  "trend_strength": null,
  "toy_relevance": 0,
  "plush_relevance": 0,
  "collectible_relevance": 0,
  "content_relevance": 0,
  "bazuuyu_relevance": 0,
  "audience": [],
  "themes": [],
  "visual_styles": [],
  "content_opportunities": [],
  "product_opportunities": [],
  "bazuuyu_opportunities": [],
  "risks": [],
  "reasoning": ""
}}

SCORING:

toy_relevance: 0-100
plush_relevance: 0-100
collectible_relevance: 0-100
content_relevance: 0-100
bazuuyu_relevance: 0-100

TREND STRENGTH:

If the supplied trend data already contains a numerical
trend score, preserve that value.

If there is no numerical trend score, return null.

Do NOT create a trend score yourself.

BAZUUYU RELEVANCE:

Consider:

- fit with plush products
- fit with collectible products
- character potential
- visual appeal
- social-media potential
- product-line potential
- compatibility with Bazuuyu's existing products

Keep recommendations practical and specific.
"""

    # --------------------------------------------------------
    # 5. SEND THE TREND TO GEMINI
    # --------------------------------------------------------
    #
    # Gemini can occasionally return temporary server errors,
    # such as HTTP 503, when the service is busy.
    #
    # We automatically retry the request a few times.
    # --------------------------------------------------------

    max_retries = 3

    for attempt in range(max_retries):

        try:

            print(
                f"\nAnalyzing trend with Gemini "
                f"(attempt {attempt + 1}/{max_retries})..."
            )

            # ------------------------------------------------
            # Send the prompt to Gemini.
            #
            # response_mime_type tells Gemini that we expect
            # machine-readable JSON.
            # ------------------------------------------------

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            # ------------------------------------------------
            # 6. CONVERT GEMINI RESPONSE TO TEXT
            # ------------------------------------------------

            text = response.text.strip()

            # ------------------------------------------------
            # 7. REMOVE MARKDOWN CODE FENCES IF PRESENT
            # ------------------------------------------------

            # Gemini may sometimes return:
            #
            # ```json
            # {
            #     ...
            # }
            # ```
            #
            # Remove those fences if they appear.

            if text.startswith("```"):

                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()

            # ------------------------------------------------
            # 8. CONVERT JSON INTO PYTHON DICTIONARY
            # ------------------------------------------------

            result = json.loads(text)

            return result

        # ----------------------------------------------------
        # HANDLE ERRORS
        # ----------------------------------------------------

        except json.JSONDecodeError as e:

            # Gemini responded, but the response was not
            # valid JSON.

            return {
                "error": "Gemini returned invalid JSON",
                "details": str(e),
                "trend": trend.get("title", ""),
                "raw_response": (
                    text if "text" in locals() else ""
                )
            }

        except Exception as e:

            error_message = str(e)

            print(
                f"Gemini request failed: {error_message}"
            )

            # ------------------------------------------------
            # Retry if we still have attempts available.
            # ------------------------------------------------

            if attempt < max_retries - 1:

                wait_seconds = 5 * (attempt + 1)

                print(
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

            else:

                # ------------------------------------------------
                # All attempts failed.
                # ------------------------------------------------

                return {
                    "error": (
                        "Gemini request failed "
                        "after retries"
                    ),
                    "details": error_message,
                    "trend": trend.get("title", "")
                }
# ============================================================
# 10. TEST THE ANALYZER
# ============================================================
#
# This test uses fake data for now.
#
# Later, we will replace this with REAL trends coming from
# Trend-Finder.
#
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Create a test trend
    # --------------------------------------------------------

    test_trend = {
        "title": "Cute animal characters",
        "description": "Social posts featuring cute animal characters.",
        "score": 82,
        "source": "test"
    }

    # --------------------------------------------------------
    # Analyze the test trend
    # --------------------------------------------------------

    result = analyze_trend(test_trend)

    # --------------------------------------------------------
    # Print the result
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("BAZUUYU TREND ANALYZER")
    print("=" * 60)

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        )
    )

    print("=" * 60)
