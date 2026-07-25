from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Form, status
from sqlalchemy.orm import Session, selectinload, joinedload
from datetime import date

from .APIlogger import logger
from .db import get_db, Furniture, Orders, Order_items
from .model import ErrorResponse, OrderDetailOut
from .sender import get_sender, Sender


router_orders = APIRouter(
    prefix="/orders",
    tags=["orders"]
)


_WITH_ITEMS = selectinload(Orders.items).joinedload(Order_items.furniture)

@router_orders.get(
    '/',
    response_model=list[OrderDetailOut],
    summary="Client orders",
    response_description="Orders with client email",
    responses={
        404: {"model": ErrorResponse, "description": "No orders with provided email"},
        422: {"model": ErrorResponse, "description": "Email does not match provided pattern"}
    },
    operation_id="get_client_orders"
)
def get_client_orders(
        q: Annotated[
            str,
            Query( 
                    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$',
                    description='Client email to search for orders',
                    examples=['ivan@example.com']
                )
        ],
        db: Session = Depends(get_db)
    ):
    '''
    Returns all orders placed on client email.

    If no orders was placed on provided email raises 404.
    '''

    orders = db.query(Orders).options(_WITH_ITEMS).filter(Orders.email == q).all()
    logger.info(f'GET /orders/?q={q}')

    if orders == []:
        logger.warning(f'User with email: {q} didn\'t make orders')
        raise HTTPException(status_code=404, detail='Orders not found')
    
    logger.info(f'Showing orders of user with email: {q}')
    return orders


@router_orders.post(
    '/',
    response_model=OrderDetailOut,
    status_code=status.HTTP_201_CREATED,
    summary='Place an order',
    response_description='Created order with its items',
    responses={
        404: {"model": ErrorResponse, "description": "One of the ordered items is not in catalog"},
        422: {"model":ErrorResponse, "description": "Email or order does not match provided pattern"}
    },
    operation_id='create_order',
)
def create_order(
        email : Annotated[
                str,
                Form(
                    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$',
                    description='Customer email. Order summary will be sent there.',
                    examples=['ivan@example.com']
                )
            ],
        items : Annotated[
            str,
            Form(
                pattern=r'^\d+,\d+(;\d+,\d+)*$',
                description=(
                    'Order items as a single string: `id,quantity` pairs separated by `;`. '
                    'For example `1,2;5,1` means two pieces of item 1 and one piece of item 5.'
                ),
                examples=['1,2;5,1'],
            )
        ],
        db: Session = Depends(get_db),
        sender: Sender = Depends(get_sender)
    ):
    '''
    Places an order and emails the customer a summary.

    Steps:
    
    1. `items` is parsed into `id,quantity` pairs.
    2. Name and price are looked up in the catalog for every ID.
    3. Total is calculated, the order and its items are stored.
    4. A summary email is sent to the given address.

    Raises `404` if any of the ordered items is not in the catalog — the order is not created.
    '''
    logger.info('POST /orders/')

    total = 0
    order_items = dict()

    for i in items.split(';'):
        str_id, str_qty = i.split(',')
        id, qty = int(str_id), int(str_qty)

        res = db.query(Furniture.name, Furniture.price).filter(Furniture.id == id).first()
        if res is None:
            logger.warning('One of the furniture in order didn\'t exist')
            raise HTTPException(status_code=404, detail='Furniture not found')
        name, price = res
        
        total += price * qty
        if id in order_items.keys():
            new_qty = order_items[id][3] + qty
            order_items[id] = (name, price, id, new_qty)
        else:
            order_items[id] = (name, price, id, qty)
    
    order = Orders(email=email, total_price=total, date=date.today())
    db.add(order)
    db.flush()

    order_str = 'Your order is:\n'
    for item in order_items.values():
        name, price, id, qty = item
        order_str += f'  - {name} (price:{price}$, quantity:{qty}), total: {price*qty}$\n'
        db.add(Order_items(order_id=order.id, furniture_id=id, quantity=qty))
    order_str += f'Total summ: {total}$'

    order_id = order.id
    db.commit()
    order = db.query(Orders).options(_WITH_ITEMS).filter(Orders.id == order_id).first()

    sender.send_email(order_str, email)

    logger.info('Successfuly create an order. Showing created order')
    return order