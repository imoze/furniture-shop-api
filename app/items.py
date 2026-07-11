from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from APIlogger import logger
from db import get_db, Furniture
from model import ErrorResponse, FurnitureOut

router_furniture = APIRouter(
    prefix="/furniture",
    tags=["furniture"]
)

@router_furniture.get(
    '/',
    response_model=list[FurnitureOut],
    summary='Furniture list',
    response_description='Furniture that satisfies query',
    operation_id='get_furniture'
)
def get_furniture(
    category: Annotated[
        str,
        Query(
            description='Filter by furniture category. Empty - list of all furniture.',
            examples=['chairs']
        )
    ] = '',
    db: Session = Depends(get_db)
):
    '''
    Returns furniture list.

    If provided a `category` returns selected category, else returns all.
    If provided a non-existing category returns empty list.
    '''
    if category == '':
        logger.info('GET /furniture/')
        logger.info('No category provided, showing all furniture.')
        return db.query(Furniture).all()
    
    logger.info(f'GET /furniture/?category={category}')
    logger.info(f'Category provided, showing: {category}.')
    return db.query(Furniture).filter(Furniture.category == category).all()

@router_furniture.get(
    '/{id}',
    response_model=FurnitureOut,
    summary='Furniture by ID',
    response_description='Selected furniture',
    responses={
        404: {"model": ErrorResponse, "description": "No furniture with provided ID"},
    },
    operation_id='get_furniture_by_id'
)
def get_furniture_by_id(
        id: Annotated[int, Path(description='Internal furniture ID', ge=1, examples=[1])],
        db: Session = Depends(get_db)
    ):
    '''
    Returns furniture by its ID.

    If furniture with provided id doesn't exist raises 404. 
    '''
    item = db.query(Furniture).filter(Furniture.id == id).first()
    logger.info(f'GET /furniture/{id}')

    if item is None: 
        logger.warning(f'Furniture with id: {id} didn\'t exist')
        raise HTTPException(status_code=404, detail='Furniture not found')
    
    logger.info(f'Showing item with id: {id}.')
    return item