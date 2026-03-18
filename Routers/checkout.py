import oracledb
from fastapi import APIRouter, Depends, HTTPException, status
from models import OrderIn, OrderOut
from database import get_db


router = APIRouter(prefix='/checkout', tags=['CHECKOUT'])

@router.post('/', status_code=status.HTTP_201_CREATED)
def add_order(new_order: OrderIn, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            order_id = cursor.var(int)
            cursor.callproc('p_add_order', [new_order.customer_name,
                                             new_order.customer_number,
                                             new_order.customer_city,
                                             new_order.customer_address,
                                             new_order.customer_bill,
                                             new_order.product_id,
                                             order_id
                                             ])
        result = {
            'order_id' : order_id.getvalue(),
            'customer_name': new_order.customer_name,
            'customer_address': new_order.customer_address,
            'customer_bill': new_order.customer_bill,
            'product_id': new_order.product_id
        }

        return result

    except oracledb.Error as e:
        print(f'Error Regarding DataBase: {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to process order. Please try again later.')


@router.get('/', response_model=list[OrderOut])
def display_order(db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            data = cursor.var(oracledb.CURSOR)

            cursor.callproc('p_display_order', [data])
            out_cursor = data.getvalue()
            rows = out_cursor.fetchall()

            out_cursor.close()

            orders = []

            for row in rows:

                result = {

                    'customer_name': row[0],
                    'customer_number': row[1],
                    'customer_city': row[2],
                    'customer_address': row[3],
                    'customer_bill': row[4],
                    'order_date': row[5],
                    'product_id': row[6],
                    'order_id' : row[7]
                }

                orders.append(result)

        return orders

    except oracledb.Error as e:
        print(f'Error for fetching checkout data {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to load orders data. Please try again later.')