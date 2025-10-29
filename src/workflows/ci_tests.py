from fastapi.testclient import TestClient
from main import app
import json, os, tempfile, shutil
import src.validators as val

client = TestClient(app)

def setup_module(module):
    module.tmpdir = tempfile.mkdtemp()
    module.datafile = os.path.join(module.tmpdir, "data.json")
    with open(module.datafile, "w") as f:
        json.dump({}, f)
    val.DATA_PATH = module.datafile  # apuntar a archivo temporal

def teardown_module(module):
    shutil.rmtree(module.tmpdir)

def test_create_and_pay_paypal():
    r = client.post("/payments/1", params={"amount": 2000, "payment_method": "paypal"})
    assert r.status_code == 200
    assert r.json()["status"] == "REGISTRADO"

    rpay = client.post("/payments/1/pay")
    assert rpay.status_code == 200
    assert rpay.json()["status"] == "PAGADO"

def test_paypal_fail_and_revert():
    r = client.post("/payments/2", params={"amount": 6000, "payment_method": "paypal"})
    assert r.status_code == 200

    rpay = client.post("/payments/2/pay")
    assert rpay.json()["status"] == "FALLIDO"

    rrev = client.post("/payments/2/revert")
    assert rrev.json()["status"] == "REGISTRADO"

def test_credit_card_validation():
    r = client.post("/payments/3", params={"amount": 200, "payment_method": "tarjeta"})
    assert r.status_code == 200
    assert r.json()["status"] == "REGISTRADO"

    # Segundo pago con tarjeta debería fallar al pagar
    r2 = client.post("/payments/4", params={"amount": 300, "payment_method": "tarjeta"})
    client.post("/payments/4/pay")
    data = val.load_payment("4")
    assert data["status"] == "FALLIDO"
