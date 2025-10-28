from fastapi import FastAPI, Query, HTTPException
from src.base import load_all_payments, save_payment, load_payment, payment_exists
from src.base import STATUS_REGISTRADO
from src.base import AMOUNT, PAYMENT_METHOD, STATUS

from src.payment_context import PaymentContext

def _get_ctx_or_404(payment_id: str) -> PaymentContext:
    try:
        data = load_payment(payment_id=payment_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f'El pago {payment_id} no existe.')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return PaymentContext(
        payment_id=payment_id,
        amount=data[AMOUNT],
        payment_method=data[PAYMENT_METHOD],
        status=data[STATUS]
    )

app = FastAPI() 

@app.get('/')
async def root():
    return {'message': 'Endpoint de prueba.'}

@app.get('/payments')
async def get_all_payments():
    all_payments = load_all_payments()
    return {'all_payments' : all_payments}

@app.post('/payments/{payment_id}', status_code=201)
async def register_payment(
    payment_id: str,                  
    amount: float = Query(..., gt=0.0), # Para asegurar monto > 0.0
    payment_method: str = Query(..., min_length=1)  # Para asegurar cadena no vacía o nula.
):
    if payment_exists(payment_id=payment_id):
        raise HTTPException(status_code=409, detail=f'El pago {payment_id} ya existe.')
    save_payment(payment_id=payment_id, amount=amount, payment_method=payment_method, status=STATUS_REGISTRADO)
    data = load_payment(payment_id=payment_id)
    return {'payment_id' : payment_id, 'data': data}

@app.post('/payments/{payment_id}/update')
async def update_payment(
    payment_id: str,
    amount: float = Query(..., gt=0.0), # Para asegurar monto > 0.0
    payment_method: str = Query(..., min_length=1)  # Para asegurar cadena no vacía o nula.
):
    ctx = _get_ctx_or_404(payment_id=payment_id)
    try:
        ctx.update(amount=amount, method=payment_method)
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))
    data = load_payment(payment_id=payment_id)
    return {'payment_id' : payment_id, 'data': data}

@app.post('/payments/{payment_id}/pay')
async def pay(payment_id: str):
    ctx = _get_ctx_or_404(payment_id=payment_id)
    try:
        ctx.pay()
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))
    data = load_payment(payment_id=payment_id)
    return {'payment_id' : payment_id, 'data': data}

@app.post('/payments/{payment_id}/revert')
async def revert(payment_id: str):
    ctx = _get_ctx_or_404(payment_id=payment_id)
    try:
        ctx.revert()
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))
    data = load_payment(payment_id=payment_id)
    return {'payment_id' : payment_id, 'data': data}




