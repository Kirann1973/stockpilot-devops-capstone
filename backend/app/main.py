from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import Product
from .schemas import ProductCreate, ProductOut, ProductUpdate, StatsOut, StockAdjust

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Inventory management API for the StockPilot DevOps capstone.",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


def _get_or_404(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/")
def root():
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health")
def health():
    """Liveness: the process is up and serving HTTP."""
    return {"status": "UP"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    """Readiness: the database is reachable, so traffic can be served."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - exercised only when the DB is down
        raise HTTPException(status_code=503, detail="Database not reachable") from exc
    return {"status": "READY"}


@app.get("/api/products", response_model=list[ProductOut])
def list_products(
    q: str | None = Query(default=None, description="Search name, SKU or supplier"),
    category: str | None = None,
    low_stock: bool = False,
    db: Session = Depends(get_db),
):
    stmt = select(Product)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Product.name.ilike(like), Product.sku.ilike(like), Product.supplier.ilike(like)))
    if category:
        stmt = stmt.where(Product.category == category)
    if low_stock:
        stmt = stmt.where(Product.quantity <= Product.reorder_level)
    return list(db.scalars(stmt.order_by(Product.id.desc())))


@app.get("/api/products/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    products = list(db.scalars(select(Product)))
    value = sum((Decimal(p.unit_price) * p.quantity for p in products), Decimal("0"))
    return StatsOut(
        total_products=len(products),
        total_units=sum(p.quantity for p in products),
        inventory_value=float(round(value, 2)),
        low_stock=sum(1 for p in products if 0 < p.quantity <= p.reorder_level),
        out_of_stock=sum(1 for p in products if p.quantity == 0),
        categories=len({p.category for p in products}),
    )


@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, product_id)


@app.post("/api/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    if db.scalar(select(func.count(Product.id)).where(Product.sku == payload.sku)):
        raise HTTPException(status_code=409, detail=f"SKU {payload.sku} already exists")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.put("/api/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = _get_or_404(db, product_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@app.post("/api/products/{product_id}/adjust", response_model=ProductOut)
def adjust_stock(product_id: int, payload: StockAdjust, db: Session = Depends(get_db)):
    product = _get_or_404(db, product_id)
    new_quantity = product.quantity + payload.delta
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Not enough stock for this adjustment")
    product.quantity = new_quantity
    db.commit()
    db.refresh(product)
    return product


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = _get_or_404(db, product_id)
    db.delete(product)
    db.commit()
