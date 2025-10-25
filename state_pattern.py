
# ==============================
# Patrón State
# =============================
from payment_validator import (
    get_validator, save_payment_data,
    STATUS_REGISTRADO, STATUS_PAGADO, STATUS_FALLIDO,
    AMOUNT, PAYMENT_METHOD, STATUS
)

class PaymentState:
    def pay(self, context): raise NotImplementedError
    def update(self, context, amount, method): raise NotImplementedError
    def revert(self, context): raise NotImplementedError

class RegisteredState(PaymentState):
    def pay(self, context):
        validator = get_validator(context.payment_method)
        valid = validator.validate(context.payment_id, context.amount, context.payment_method)
        if valid:
            context.status = STATUS_PAGADO
            context.set_state(PaidState())
        else:
            context.status = STATUS_FALLIDO
            context.set_state(FailedState())
        context._persist()

    def update(self, context, amount, method):
        context.amount = amount
        context.payment_method = method
        context._persist()

    def revert(self, context):
        raise Exception("No se puede revertir un pago REGISTRADO")

class PaidState(PaymentState):
    def pay(self, context): raise Exception("El pago ya está PAGADO")
    def update(self, context, amount, method): raise Exception("No se puede actualizar un pago PAGADO")
    def revert(self, context): raise Exception("No se puede revertir un pago PAGADO")

class FailedState(PaymentState):
    def pay(self, context):
        validator = get_validator(context.payment_method)
        valid = validator.validate(context.payment_id, context.amount, context.payment_method)
        if valid:
            context.status = STATUS_PAGADO
            context.set_state(PaidState())
        else:
            context.status = STATUS_FALLIDO
        context._persist()

    def update(self, context, amount, method):
        raise Exception("No se puede actualizar un pago FALLIDO")

    def revert(self, context):
        context.status = STATUS_REGISTRADO
        context.set_state(RegisteredState())
        context._persist()

# evitar circular import
from payment_context import PaymentContext  # noqa: E402
