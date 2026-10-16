from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

StockStatus = Literal["IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK"]


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=64)
    category: str = "General"
    supplier: str = "Unknown"
    description: str = ""
    quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0, max_digits=10, decimal_places=2)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = None
    supplier: str | None = None
    description: str | None = None
    quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)
    unit_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)


class StockAdjust(BaseModel):
    """Positive delta = goods received, negative delta = goods shipped."""

    delta: int
    reason: str = "manual adjustment"


class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def stock_status(self) -> StockStatus:
        if self.quantity == 0:
            return "OUT_OF_STOCK"
        if self.quantity <= self.reorder_level:
            return "LOW_STOCK"
        return "IN_STOCK"


class StatsOut(BaseModel):
    total_products: int
    total_units: int
    inventory_value: float
    low_stock: int
    out_of_stock: int
    categories: int
