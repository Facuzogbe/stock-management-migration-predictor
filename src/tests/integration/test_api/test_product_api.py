import json
from unittest.mock import patch
from src.models import ProductMasterData as Product

# Test para obtener todos los productos (GET /api/products/)
# Verifica que se pueda obtener correctamente la lista de productos en formato JSON.
def test_get_all_products(client):
    response = client.get("/api/products/")
    assert response.status_code == 200
    assert isinstance(response.json, list)

# Test para crear un nuevo producto con datos válidos (POST /api/products/)
# Verifica que el producto se cree correctamente y que se retorne status 201.
def test_create_product(client):
    response = client.post("/api/products/", json={
        "product_id": "p001",
        "product_name": "Producto Test",
        "sku": "SKU001",
        "unit_of_measure": "unidad",
        "cost": 10.0,
        "sale_price": 20.0,
        "category": "Categoria A",
        "location": "Estante 1",
        "active": True
    })
    assert response.status_code == 201
    assert response.json["message"] == "Producto creado correctamente."

# Test para crear un producto con datos inválidos (POST /api/products/)
# Fuerza un error pasando un campo faltante o inválido para cubrir el except.
def test_create_product_invalid_data(client):
    response = client.post("/api/products/", json={
        # Falta el campo product_id, lo que debería causar un KeyError
        "product_name": "Producto Malo"
    })
    assert response.status_code == 400
    assert "error" in response.json

# Test para actualizar un producto existente (PUT /api/products/<product_id>)
# Verifica que se pueda actualizar correctamente y que retorne status 200.
def test_update_product_success(client):
    # Primero se crea un producto
    client.post("/api/products/", json={
        "product_id": "p002",
        "product_name": "Original",
        "sku": "SKU002",
        "unit_of_measure": "unidad",
        "cost": 5.0,
        "sale_price": 15.0,
        "category": "Cat",
        "location": "Loc",
    })

    # Luego se actualiza el producto
    response = client.put("/api/products/p002", json={
        "product_name": "Modificado",
        "cost": 8.5
    })
    assert response.status_code == 200
    assert response.json["product"]["product_name"] == "Modificado"

# Test para intentar actualizar un producto inexistente (PUT /api/products/<product_id>)
# Verifica que si el ID no existe, se retorne status 404.
def test_update_product_not_found(client):
    response = client.put("/api/products/9999", json={})
    assert response.status_code == 404

# Test para actualizar un producto con datos inválidos (PUT /api/products/<product_id>)
# Verifica que si se pasa un valor no convertible a float, se capture la excepción y retorne 400.
def test_update_product_invalid_data(client):
    client.post("/api/products/", json={
        "product_id": "p003",
        "product_name": "Producto",
        "sku": "SKU003",
        "unit_of_measure": "unidad",
        "cost": 10.0,
        "sale_price": 20.0,
        "category": "Cat",
        "location": "Loc",
    })

    response = client.put("/api/products/p003", json={
        "cost": "no_es_float"
    })
    assert response.status_code == 400
    assert "error" in response.json

# Test para eliminar un producto existente (DELETE /api/products/<product_id>)
# Verifica que el producto se elimine correctamente y se retorne status 200.
def test_delete_product_success(client):
    client.post("/api/products/", json={
        "product_id": "p004",
        "product_name": "A eliminar",
        "sku": "SKU004",
        "unit_of_measure": "unidad",
        "cost": 10.0,
        "sale_price": 20.0,
        "category": "Cat",
        "location": "Loc",
    })

    response = client.delete("/api/products/p004")
    assert response.status_code == 200
    assert "eliminado correctamente" in response.json["message"]

# Test para intentar eliminar un producto inexistente (DELETE /api/products/<product_id>)
# Verifica que si el producto no existe, se retorne status 404.
def test_delete_product_not_found(client):
    response = client.delete("/api/products/inexistente")
    assert response.status_code == 404

# Test para simular un error en la base de datos al eliminar un producto (DELETE /api/products/<product_id>)
# Se hace mock del método db.session.delete para que lance una excepción, y se verifica que se capture correctamente.
@patch("src.app.routes.api.product_api.db.session.delete", side_effect=Exception("db error"))
def test_delete_product_db_error(mock_delete, client):
    client.post("/api/products/", json={
        "product_id": "p005",
        "product_name": "Con error",
        "sku": "SKU005",
        "unit_of_measure": "unidad",
        "cost": 10.0,
        "sale_price": 20.0,
        "category": "Cat",
        "location": "Loc",
    })

    response = client.delete("/api/products/p005")
    assert response.status_code == 400
    assert "error" in response.json
