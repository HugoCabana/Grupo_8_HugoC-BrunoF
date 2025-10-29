import sys
import os
import json
import tempfile
import shutil
from fastapi.testclient import TestClient

# Asegura que el directorio raíz esté en sys.path (por si se ejecuta desde test/)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app  # importa la app FastAPI
import src.base as val

client = TestClient(app)

def setup_module(module):
    # Crear directorio temporal para el archivo data.json de test
    module.tmpdir = tempfile.mkdtemp()
    persistent_dir = os.path.join(module.tmpdir, "persistent")
    os.makedirs(persistent_dir, exist_ok=True)

    # Crear archivo JSON vacío para almacenar pagos de test
    module.datafile = os.path.join(persistent_dir, "data.json")
    with open(module.datafile, "w") as f:
        json.dump({}, f)

    # Redirigir la ruta de datos de la app hacia el archivo temporal
    val.DATA_PATH = module.datafile
    print(f" Tests usando archivo temporal: {module.datafile}")

def teardown_module(module):
    # Eliminar directorio temporal después de correr los tests
    shutil.rmtree(module.tmpdir)

def test_create_and_pay_paypal():
    """Flujo normal: crear un pago PayPal válido y pagarlo."""
    r = client.post("/payments/1", params={"amount": 2000, "payment_method": "paypal"})
    assert r.status_code == 201
    assert r.json()["data"]["status"] == "REGISTRADO"

    rpay = client.post("/payments/1/pay")
    assert rpay.status_code == 200
    assert rpay.json()["data"]["status"] == "PAGADO"

def test_paypal_fail_and_revert():
    """Pago PayPal con monto > 5000 debe fallar y poder revertirse."""
    r = client.post("/payments/2", params={"amount": 6000, "payment_method": "paypal"})
    assert r.status_code == 201

    rpay = client.post("/payments/2/pay")
    assert rpay.status_code == 200
    assert rpay.json()["data"]["status"] == "FALLIDO"

    rrev = client.post("/payments/2/revert")
    assert rrev.status_code == 200
    assert rrev.json()["data"]["status"] == "REGISTRADO"

def test_credit_card_validation():
    """No se permiten dos pagos REGISTRADOS con tarjeta de crédito."""
    r1 = client.post("/payments/3", params={"amount": 200, "payment_method": "tarjeta"})
    assert r1.status_code == 201
    assert r1.json()["data"]["status"] == "REGISTRADO"

    # Segundo pago con tarjeta
    r2 = client.post("/payments/4", params={"amount": 300, "payment_method": "tarjeta"})
    assert r2.status_code == 201

    # Intentar pagar el segundo -> debe FALLAR porque ya hay uno REGISTRADO
    rpay2 = client.post("/payments/4/pay")
    assert rpay2.status_code == 200
    data = val.load_payment("4")
    assert data["status"] == "FALLIDO"
