import logging
import smtplib
from email.mime.text import MIMEText
import os
from datetime import date
from fastapi import FastAPI, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from db import Base, engine, get_db, Furniture, Orders, Order_items

logger = logging.getLogger(__name__)
logging.basicConfig(filename='app.log')

app = FastAPI()

@app.get('/furniture/')
def get_futniture(category: str = '', db: Session = Depends(get_db)):
    if category == '':
        logger.info('GET /furniture/')
        logger.info('No category provided, showing all furniture.')
        return db.query(Furniture).all()
    else:
        logger.info(f'GET /furniture/?category={category}')
        logger.info(f'Category provided, showing: {category}.')
        return db.query(Furniture).filter(Furniture.category == category).all()

@app.get('/furniture/{id}')
def get_futniture_by_id(id: int, db: Session = Depends(get_db)):
    item = db.query(Furniture).filter(Furniture.id == id).first()
    logger.info(f'GET /furniture/{id}')
    if item is None: 
        logger.warning(f'Furniture with id: {id} didn\'t exist')
        raise HTTPException(status_code=404, detail='Furniture not found')
    logger.info(f'Showing item with id: {id}.')
    return item
    

@app.get('/orders/')
def get_client_orders(q: str, db: Session = Depends(get_db)):
    orders = db.query(Orders).filter(Orders.email == q).all()
    logger.info(f'GET /orders/{q}')
    if orders == []:
        logger.warning(f'User with email: {q} didn\'t make orders')
        raise HTTPException(status_code=404, detail='Orders not found')
    logger.info(f'Showing orders of user with email: {id}')
    return orders


@app.post('/orders/')
def create_order(email : str = Form(), items : str = Form(), db: Session = Depends(get_db)):
    logger.info(f'POST /orders/')
    total = 0
    order_items = list()
    for i in items.split(';'):
        if i.split(',') != ['']:
            str_id, str_qty = i.split(',')
            id, qty = int(str_id), int(str_qty)

            res = db.query(Furniture.name, Furniture.price).filter(Furniture.id == id).first()
            if res is None:
                logger.warning('One of the furniture in order didn\'t exist')
                raise HTTPException(status_code=404, detail='Furniture not found')
            name, price = res
            
            total += price * qty
            order_items.append((name, price, id, qty))
    
    order = Orders(email=email, total_price=total, date=date.today())
    db.add(order)
    db.flush()

    order_str = 'Your order is:\n'
    for name, price, id, qty in order_items:
        order_str += f'  - {name} (price:{price}$, quantity:{qty}), total: {price*qty}$\n'
        db.add(Order_items(order_id=order.id, furniture_id=id, quantity=qty))
    order_str += f'Total summ: {total}$'

    message = MIMEText(order_str)
    message['From'] = 'furniture@shop.com'
    message['To'] = email
    message['Subject'] = 'Your order'

    with smtplib.SMTP('mailhog', 1025) as server:
        server.send_message(message)

    db.commit()
    db.refresh(order)
    logger.info('Successfuly create an order. Showing created order')
    return (order)