from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import analyzer
import db


app = FastAPI()

db.initialize_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


@app.get("/api/products/{product_id}/insight")
def get_product_insight(product_id: int):
    product = db.get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    _, title, _, _, _ = product
    metrics = analyzer.calculate_price_metrics(product_id)
    insight_text = analyzer.generate_product_insight(title or f"Product {product_id}", metrics)

    return {
        "product_id": product_id,
        "metrics": metrics,
        "ai_insight": insight_text,
    }