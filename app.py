import json

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import analyzer
import db


app = FastAPI()

db.initialize_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "API is running"}


class ProductCreate(BaseModel):
    title: str
    url: str
    target_price: float


@app.get("/api/products")
def get_products():
    products = db.get_all_products()
    return [
        {
            "id": product_id,
            "title": title,
            "url": url,
            "target_price": target_price,
            "platform": platform,
        }
        for product_id, title, url, target_price, platform in products
    ]


@app.post("/api/products")
def add_product(payload: ProductCreate):
    platform = "amazon"
    db.add_product(payload.title, payload.url, payload.target_price, platform)
    return {"message": "Product added successfully"}


@app.get("/api/products/{product_id}/history")
def get_product_history(product_id: int):
    product = db.get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    history_rows = db.get_price_history(product_id)
    return [
        {
            "id": row_id,
            "product_id": row_product_id,
            "price": price,
            "timestamp": timestamp,
        }
        for row_id, row_product_id, price, timestamp in history_rows
    ]


def _build_analysis_response(product_id: int, title: str, analysis: dict, metrics: dict):
    return {
        "product_id": product_id,
        "product_title": title,
        "metrics": metrics,
        "analysis": analysis,
    }


@app.get("/api/products/{product_id}/analysis")
@app.get("/api/products/{product_id}/insight")
def get_product_analysis(product_id: int, refresh: bool = False):
    product = db.get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    _, title, _, _, _ = product

    if not refresh:
        cached_analysis = db.get_latest_ai_analysis(product_id)
        if cached_analysis is not None:
            _, _, _, _, payload_json_string, _ = cached_analysis
            try:
                return json.loads(payload_json_string)
            except (TypeError, json.JSONDecodeError):
                pass

    try:
        metrics = analyzer.calculate_price_metrics(product_id)
        analysis = analyzer.generate_product_insight(title or f"Product {product_id}", metrics)
    except (ValueError, ImportError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Insights service is currently unavailable due to a backend configuration or API key issue.",
        )

    response_payload = _build_analysis_response(
        product_id,
        title or f"Product {product_id}",
        analysis,
        metrics,
    )

    db.log_ai_analysis(
        product_id,
        analysis.get("recommendation"),
        analysis.get("deal_score"),
        json.dumps(response_payload),
    )

    return response_payload