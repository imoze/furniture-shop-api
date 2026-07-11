from fastapi import FastAPI

from items import router_furniture
from orders import router_orders

description = '''## What it can do?
This is API to interact with goods and orders.
It provides some basic interactions:

- get all products
- get products by category
- get product by id
- get orders of user by email
- place order
'''

metadata = [
    {
        'name': 'furniture',
        'description': 'Getting information about furniture.'
    },
    {
        'name': 'orders',
        'description': 'Getting information about orders and placing them.'
    }
]

app = FastAPI(
    title = 'Furniture Shop Basic API',
    summary = 'Result of completing test task of job interview',
    description = description,
    version = '0.2.0',
    openapi_tags = metadata,
    contact={'name': 'Andrew', 'email': 'game-f-90@mail.ru'},
    swagger_ui_parameters={
        'docExpansion': 'none',
        'displayRequestDuration': True,
        'tryItOutEnabled': True,
    }
)

app.include_router(router_furniture)
app.include_router(router_orders)