# MIA203 - Ingeniería de Software y de Datos (grupo 2025)

## Examen Unidad 1 

## Grupo 8 : Hugo Cabaña - Bruno Francisco Barra Atarama

## Algunas decisiones tomadas:

- Separamos la API con sus endpoint en `main.py` de `base.py` y `state.py`, que contiene rutinas provistas en la consigna y las clases con sus métodos para llevar a cabo el procesamiento de pagos con el patrón de diseño por estados.

## Nomenclatura:

`feat/`: en ramas, indica que es una rama de desarrollo de una *feature* que responda a un *issue*.

Aqui aplicamos trabajo colaborativo diviendo el trabajo en tareas (issues) y luego solicitando `Pull request`. Una vez que el compañero revisaba el PR comentaba y si no habia conflictos aceptaba y daba el `merge to main`.

### Plan de desarrollo

1. Diseño con patrón State

- Creamos una clase PaymentContext que representará un pago.

- Definimos una interfaz PaymentState con operaciones (pay, update, revert).

- Implementamos los estados concretos:

    - RegisteredState
    
    - PaidState

    - FailedState

- Cada estado define qué acciones son válidas.

2. Validación por método de pago

- Clase PaymentValidator con subclases:

    - CreditCardValidator

    - PayPalValidator

- Cada una implementa su validación según el enunciado.

3. Persistencia

- Usamos un data.json (como en el código base del examen) para almacenar los pagos.

4. Endpoints

- GET /payments → listar todos.

- POST /payments/{id} → crear pago (estado REGISTRADO).

- POST /payments/{id}/update → actualizar monto o método (solo si REGISTRADO).

- POST /payments/{id}/pay → validar y pagar.

- POST /payments/{id}/revert → revertir de FALLIDO → REGISTRADO.

5. Tests unitarios

- Usaremos pytest para probar:

    - Creación y validación de pago correcto.

    - Validación fallida (por monto o duplicado).

    - Reversión de pago fallido y reintento exitoso.

### Instrucciones para el uso de la API 

1. Crear y activar entorno virtual:
```
python -m venv .venv
source .venv/bin/activate    # linux/mac
.venv\Scripts\activate       # windows
pip install -r requirements.txt
```

2. Correr la API:
```
uvicorn main:app --reload --port 8000
# luego abrir http://127.0.0.1:8000/docs para probar
```

3. Ejecutar tests:
```
pytest -q
```


### Notas de diseño / trade-offs 

Usamos State pattern para modelar comportamiento según estado (Registered/Paid/Failed) en PaymentContext. Esto mantiene las reglas de transición encapsuladas en cada estado.

Los validadores son clases separadas; la función `get_validator` decide qué validador usar según nombre del `payment_method`. Esto hace fácil agregar nuevos métodos.

Persistencia simple con JSON (data.json) para cumplir la consigna; pero esto esto no es concurrente, en producción se debe usar una Base de datos.

En el validador de tarjeta se chequea que no haya más de 1 pago en estado REGISTRADO con el mismo `payment_method`. La condición enunciada decía "no haya más de 1 pago con este medio de pago en estado REGISTRADO" — interpretamos que eso implica solo un registro permitido a la vez; el test refleja esta lógica.

Los tests unitarios se implementaron usando pytest y cubren los flujos principales de la API:

- Creación de pagos y validaciones por método (tarjeta / PayPal).

- Transiciones de estado (REGISTRADO → PAGADO / FALLIDO).

- Reversión de pagos fallidos y reintento exitoso.

Cada test utiliza un archivo data.json temporal, por lo que no modifica los datos reales del entorno de desarrollo.

Para facilitar esto se incluyó `set_data_path_for_tests(path)`.

Durante las pruebas, esta función redirige el almacenamiento de datos hacia un archivo temporal, asegurando que los tests no modifiquen el entorno real.