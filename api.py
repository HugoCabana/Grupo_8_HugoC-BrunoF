from fastapi import FastAPI, Query, HTTPException
from main import load_all_payments, save_payment, load_payment, save_payment_data
from main import STATUS, AMOUNT, PAYMENT_METHOD
from main import STATUS_REGISTRADO, STATUS_FALLIDO, STATUS_PAGADO

from payment_context import PaymentContext
# from main import DATA_PATH
app = FastAPI() 

@app.get('/')
async def root():
    return {'message': 'Endpoint de prueba.'}

@app.get('/payments')
async def get_all_payments():
    all_payments = load_all_payments()
    return {'all_payments' : all_payments}

@app.post('/payments/{payment_id}')
async def register_payment(
    payment_id: str,                  
    amount: float = Query(...),       
    payment_method: str = Query(...)
):
    
    save_payment(payment_id=payment_id, amount=amount, payment_method=payment_method, status=STATUS_REGISTRADO)
    data = load_payment(payment_id=payment_id)
    return {'payment_id' : payment_id, 'data': data}

@app.post('/payments/{payment_id}/update')
async def update_payment(
    payment_id: str,
    amount: float = Query(...),
    payment_method: str = Query(...),
):
    try:
        data = load_payment(payment_id=payment_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error al cargar el pago para actualizarlo {e}.')
    data[AMOUNT] = amount
    data[PAYMENT_METHOD] = payment_method
    save_payment_data(payment_id=payment_id, data=data)
    return {'payment_id' : payment_id, 'data': data}

@app.post('/payments/{payment_id}/')
async def pay(payment_id: str):
    try:
        data = load_payment(payment_id=payment_id)
        ctx = PaymentContext(
                payment_id=payment_id,
                amount=data["amount"],
                payment_method=data["payment_method"],
                status=data["status"]
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error al cargar el pago {e}.')

    try:
        ctx.pay()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error al procesar el pago {e}')

@app.post('/payments/{payment_id}/revert')
async def revert(payment_id: str):
    try:
        data = load_payment(payment_id=payment_id)
        ctx = PaymentContext(
                payment_id=payment_id,
                amount=data["amount"],
                payment_method=data["payment_method"],
                status=data["status"]
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error al cargar el pago {e}.')

    try:
        ctx.revert()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error al revertir el pago {e}')





