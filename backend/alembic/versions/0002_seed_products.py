"""seed demo inventory

Revision ID: 0002_seed_products
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_seed_products"
down_revision = "0001_create_products"
branch_labels = None
depends_on = None

products = sa.table(
    "products",
    sa.column("name", sa.String),
    sa.column("sku", sa.String),
    sa.column("category", sa.String),
    sa.column("supplier", sa.String),
    sa.column("quantity", sa.Integer),
    sa.column("reorder_level", sa.Integer),
    sa.column("unit_price", sa.Numeric),
)

SEED = [
    ("Wireless Mouse", "ELEC-1001", "Electronics", "TechSource", 120, 25, 499.00),
    ("USB-C Charger 65W", "ELEC-1002", "Electronics", "TechSource", 18, 20, 1299.00),
    ("A4 Copier Paper (500)", "OFF-2001", "Office", "PaperMart", 0, 30, 289.00),
    ("Ergonomic Chair", "FURN-3001", "Furniture", "SitWell", 9, 5, 7499.00),
    ("Whiteboard Markers (4)", "OFF-2002", "Office", "PaperMart", 64, 15, 149.00),
    ("27\" Monitor", "ELEC-1003", "Electronics", "ViewPro", 4, 6, 15999.00),
]


def upgrade():
    op.bulk_insert(
        products,
        [
            dict(name=n, sku=s, category=c, supplier=sup, quantity=q, reorder_level=r, unit_price=p)
            for n, s, c, sup, q, r, p in SEED
        ],
    )


def downgrade():
    op.execute(products.delete().where(products.c.sku.in_([row[1] for row in SEED])))
