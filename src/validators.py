import json
import os

from src.base import DATA_PATH, STATUS, AMOUNT, PAYMENT_METHOD, STATUS_REGISTRADO

# -------------------------------
# Persistencia
# -------------------------------
def ensure_datafile():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({}, f)

def load_all_payments():
    ensure_datafile()
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_all_payments(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def load_payment(payment_id):
    data = load_all_payments()
    if str(payment_id) not in data:
        raise KeyError(f"Payment {payment_id} not found")
    return data[str(payment_id)]

def save_payment_data(payment_id, data):
    all_data = load_all_payments()
    all_data[str(payment_id)] = data
    save_all_payments(all_data)

def save_payment(payment_id, amount, payment_method, status):
    data = {AMOUNT: amount, PAYMENT_METHOD: payment_method, STATUS: status}
    save_payment_data(payment_id, data)

# -------------------------------
# Validadores de métodos de pago
# -------------------------------
class PaymentValidator:
    def validate(self, payment_id, amount, payment_method):
        raise NotImplementedError

class CreditCardValidator(PaymentValidator):
    def validate(self, payment_id, amount, payment_method):
        if amount >= 10000:
            return False
        # no más de un pago REGISTRADO con tarjeta
        payments = load_all_payments()
        registrados = [p for p in payments.values()
                       if p[PAYMENT_METHOD] == payment_method and p[STATUS] == STATUS_REGISTRADO]
        return len(registrados) < 1

class PayPalValidator(PaymentValidator):
    def validate(self, payment_id, amount, payment_method):
        return amount < 5000

def get_validator(payment_method: str):
    method = payment_method.lower()
    if "tarjeta" in method or "card" in method:
        return CreditCardValidator()
    elif "paypal" in method:
        return PayPalValidator()
    return PaymentValidator()  # sin validación
