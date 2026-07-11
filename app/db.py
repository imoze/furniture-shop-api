import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import Table, Column, Integer, Numeric, Text, Date, ForeignKey

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

Base = declarative_base()

class Furniture(Base):
    __tablename__ = 'furniture'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    price = Column(Numeric(10,2),nullable=False)
    category = Column(Text, nullable=False)

class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, nullable=False)
    total_price = Column(Numeric(12,2),nullable=False)
    date = Column(Date, nullable=False)

    items = relationship('Order_items', back_populates='order')

class Order_items(Base):
    __tablename__ = 'order_items'
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    furniture_id = Column(Integer, ForeignKey('furniture.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)

    order = relationship('Orders', back_populates='items')
    furniture = relationship('Furniture')

    @property
    def name(self) -> str:
        return self.furniture.name

    @property
    def price(self):
        return self.furniture.price

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()