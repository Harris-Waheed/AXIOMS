import oracledb
from fastapi import APIRouter, Depends, HTTPException, status
from models import OrderIn, OrderOut
from database import get_db


router = APIRouter(prefix='/checkout', tags=['CHECKOUT'])

@router.post('/', response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def add_order(new_order: OrderIn, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            cursor.call_proc('p_add_order', [new_order.customer_name,
                                             new_order.customer_number,
                                             new_order.customer_city,
                                             new_order.customer_address,
                                             new_order.customer_bill
                                             ])
        result = {
            'customer_name': new_order.customer_name,
            'customer_address': new_order.customer_address,
            'customer_bill': new_order.customer_bill
        }

        return result

    except oracledb.Error as e:
        print(f'Error Regarding DataBase: {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to process order. Please try again later.')