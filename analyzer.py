import os
import json
import logging
import sqlite3

from dotenv import load_dotenv

import db


load_dotenv()


def calculate_price_metrics(product_id):
    """Calculate aggregate price metrics for a product's full price history."""
    with sqlite3.connect(db.DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute(
            """
            SELECT price
            FROM price_history
            WHERE product_id = ?
            ORDER BY timestamp ASC, id ASC
            """,
            (product_id,),
        )
        prices = [row[0] for row in cursor.fetchall()]

    if not prices:
        return {
            "current_price": None,
            "historical_max": None,
            "historical_min": None,
            "average_price": None,
            "pct_drop_from_max": None,
        }

    current_price = prices[-1]
    historical_max = max(prices)
    historical_min = min(prices)
    average_price = sum(prices) / len(prices)

    if historical_max and historical_max != 0:
        pct_drop_from_max = ((historical_max - current_price) / historical_max) * 100
    else:
        pct_drop_from_max = 0.0

    return {
        "current_price": current_price,
        "historical_max": historical_max,
        "historical_min": historical_min,
        "average_price": average_price,
        "pct_drop_from_max": pct_drop_from_max,
    }


def generate_product_insight(product_title, metrics):
    """Generate a concise shopping recommendation from price metrics using an LLM."""
    # LLM INTEGRATION: Change this import/client section if you switch providers or model families.
    try:
        from google import genai
    except ImportError as exc:
        raise ImportError(
            "The 'google-genai' package is required for generate_product_insight. Install it with: pip install google-genai"
        ) from exc

    # LLM INTEGRATION: Set TRACKER_KEY in your environment or .env file for Gemini access.
    api_key = os.getenv("TRACKER_KEY")
    if not api_key:
        raise ValueError("TRACKER_KEY is not set.")

    # LLM INTEGRATION: Change the Gemini model here or override it with TRACKER_MODEL.
    model_name = os.getenv("TRACKER_MODEL", "gemini-3.5-flash")
    client = genai.Client(api_key=api_key)

    current_price = metrics.get("current_price")
    historical_max = metrics.get("historical_max")
    historical_min = metrics.get("historical_min")
    average_price = metrics.get("average_price")

    fallback_insight = {
        "recommendation": "NEUTRAL",
        "confidence": 0.0,
        "predicted_direction": "stable",
        "predicted_range": {"low": 0.0, "high": 0.0},
        "deal_score": 0,
        "rationale": "Unable to generate a reliable AI insight from the current model response.",
    }

    def _fmt_price(value):
        if value is None:
            return "N/A"
        return f"${value:.2f}"

    strict_prompt = (
        "You are a cynical, smart e-commerce shopping assistant. "
        "Use only the provided pricing data. "
        "Return only valid JSON that strictly matches this schema layout: "
        '{"recommendation":"BUY_NOW|WAIT|NEUTRAL","confidence":0.0,"predicted_direction":"down|up|stable","predicted_range":{"low":0.0,"high":0.0},"deal_score":0,"rationale":"string explanation"}. '
        "Do not wrap the JSON in markdown, code fences, or extra commentary."
    )

    user_prompt = (
        "Product pricing snapshot:\n"
        f"Title: {product_title}\n"
        f"Current Price: {_fmt_price(current_price)}\n"
        f"Historic High: {_fmt_price(historical_max)}\n"
        f"Historic Low: {_fmt_price(historical_min)}\n"
        f"Average Price: {_fmt_price(average_price)}\n\n"
        "Generate the insight now."
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=f"{strict_prompt}\n\n{user_prompt}",
            response_mime_type="application/json",
        )

        content = getattr(response, "text", None)
        if content:
            parsed_content = json.loads(content.strip())
            recommendation = parsed_content["recommendation"]
            confidence = parsed_content["confidence"]
            predicted_direction = parsed_content["predicted_direction"]
            predicted_range = parsed_content["predicted_range"]
            deal_score = parsed_content["deal_score"]
            rationale = parsed_content["rationale"]

            return {
                "recommendation": recommendation,
                "confidence": confidence,
                "predicted_direction": predicted_direction,
                "predicted_range": {
                    "low": predicted_range["low"],
                    "high": predicted_range["high"],
                },
                "deal_score": deal_score,
                "rationale": rationale,
            }
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return fallback_insight
    except Exception:
        logging.exception("Failed to generate AI product insight due to an external API or network error.")
        return fallback_insight

    if current_price is None:
        return fallback_insight

    if historical_max is not None and current_price <= historical_max * 0.9:
        recommendation = "BUY_NOW"
        verdict = "The price is sitting well below the recent ceiling, which is usually where shoppers stop overthinking."
    elif average_price is not None and current_price > average_price:
        recommendation = "WAIT"
        verdict = "The current price is above average, so patience still has a job to do here."
    else:
        recommendation = "NEUTRAL"
        verdict = "The numbers are not screaming either way, so a closer look is still warranted."

    return {
        "recommendation": recommendation,
        "confidence": 0.5,
        "predicted_direction": "stable",
        "predicted_range": {
            "low": current_price if current_price is not None else 0.0,
            "high": current_price if current_price is not None else 0.0,
        },
        "deal_score": 50 if recommendation == "NEUTRAL" else 75 if recommendation == "BUY_NOW" else 25,
        "rationale": verdict,
    }
