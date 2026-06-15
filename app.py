from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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