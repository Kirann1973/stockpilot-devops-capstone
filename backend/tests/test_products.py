def test_create_product(client, product):
    assert product["id"] > 0
    assert product["sku"] == "TEST-001"
    assert product["stock_status"] == "IN_STOCK"


def test_duplicate_sku_is_rejected(client, product):
    response = client.post("/api/products", json={"name": "Copy", "sku": "TEST-001"})
    assert response.status_code == 409


def test_negative_quantity_fails_validation(client):
    response = client.post("/api/products", json={"name": "Bad", "sku": "BAD-1", "quantity": -5})
    assert response.status_code == 422


def test_list_and_get_product(client, product):
    listed = client.get("/api/products").json()
    assert [p["sku"] for p in listed] == ["TEST-001"]
    fetched = client.get(f"/api/products/{product['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Wireless Mouse"


def test_get_missing_product_returns_404(client):
    assert client.get("/api/products/9999").status_code == 404


def test_update_product_marks_low_stock(client, product):
    response = client.put(f"/api/products/{product['id']}", json={"quantity": 5})
    assert response.status_code == 200
    assert response.json()["stock_status"] == "LOW_STOCK"


def test_adjust_stock_receive_and_ship(client, product):
    received = client.post(f"/api/products/{product['id']}/adjust", json={"delta": 25})
    assert received.json()["quantity"] == 75
    too_many = client.post(f"/api/products/{product['id']}/adjust", json={"delta": -100})
    assert too_many.status_code == 400


def test_delete_product(client, product):
    assert client.delete(f"/api/products/{product['id']}").status_code == 204
    assert client.get(f"/api/products/{product['id']}").status_code == 404


def test_search_and_low_stock_filter(client, product):
    client.post("/api/products", json={"name": "Paper", "sku": "OFF-1", "quantity": 2, "reorder_level": 10})
    assert [p["sku"] for p in client.get("/api/products?q=paper").json()] == ["OFF-1"]
    assert [p["sku"] for p in client.get("/api/products?low_stock=true").json()] == ["OFF-1"]


def test_stats(client, product):
    client.post("/api/products", json={"name": "Paper", "sku": "OFF-1", "category": "Office", "quantity": 0})
    stats = client.get("/api/products/stats").json()
    assert stats["total_products"] == 2
    assert stats["total_units"] == 50
    assert stats["inventory_value"] == 24950.0
    assert stats["out_of_stock"] == 1
    assert stats["categories"] == 2
