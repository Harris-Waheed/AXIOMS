import oracledb
from fastapi import APIRouter, Depends, HTTPException, status
from models import OrderIn, OrderCustomerOut
from database import get_db


router = APIRouter(prefix='/checkout', tags=['CHECKOUT'])

@router.post('/{product_id}', status_code=status.HTTP_201_CREATED)
def add_order(product_id, new_order: OrderIn, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:

            cursor.callproc('p_verify_product', [product_id])
            product_verify = cursor.getimplicitresults()
            product = product_verify[0].fetchone()

            if product:
                order_id = cursor.var(int)
                cursor.callproc('p_add_order', [new_order.customer_name,
                                                 new_order.customer_number,
                                                 new_order.customer_city,
                                                 new_order.customer_address,
                                                 new_order.customer_bill,
                                                 new_order.product_quantity,
                                                 product_id,
                                                 order_id
                                                 ])
                result = {
                    'order_id' : order_id.getvalue(),
                    'customer_name': new_order.customer_name,
                    'customer_address': new_order.customer_address,
                    'customer_bill': new_order.customer_bill,
                    'product_id': product_id
                }

                return result

            else:
                raise HTTPException(status_code=404, detail='Product Not Exist!')

    except oracledb.Error as e:
        print(f'Error Regarding DataBase: {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to process order. Please try again later.')


@router.get('/', response_model=list[OrderCustomerOut])
def display_orders(db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            data = cursor.var(oracledb.CURSOR)

            cursor.callproc('p_display_orders', [data])
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
                    'order_id' : row[7],
                    'product_quantity' : row[8]
                }

                orders.append(result)

        return orders

    except oracledb.Error as e:
        print(f'Error for fetching checkout data {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to load orders data. Please try again later.')

@router.get('/{order_id}', response_model=OrderCustomerOut) # Created to get single order data
def display_order(order_id: int, db = Depends(get_db)):

    try:
        with db.cursor() as cursor:
            cursor.callproc('p_display_order', [order_id])

            results = cursor.getimplicitresults()
            if results:
                row = results[0].fetchone()
            else:
                row = None

    except oracledb.Error as e:
        print(f'Error Occurred: {e}')
        raise HTTPException(status_code=500, detail='Unable to load!')

    if not row:
        raise HTTPException(status_code=404, detail='Order Not Found!')

    result = {

        'customer_name': row[0],
        'customer_number': row[1],
        'customer_city': row[2],
        'customer_address': row[3],
        'customer_bill': row[4],
        'order_date': row[5],
        'order_id' : row[7],
        'product_quantity' : row[8]
                }


    return result
