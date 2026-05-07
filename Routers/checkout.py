import json
import oracledb
from uuid import uuid4
from database import get_db
from Routers.login import get_token
from fastapi import APIRouter, Depends, HTTPException, status
from models import OrderIn, OrderCustomerOut, OrderAdminOut, OrderStatus, OrderUpdateIn


router = APIRouter(prefix='/checkout', tags=['CHECKOUT'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def add_order(new_order: OrderIn, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:

            order_id = cursor.var(int)
            cursor.callproc('p_add_order',
                            [new_order.customer_name,
                             new_order.customer_number,
                             new_order.customer_city,
                             new_order.customer_address,
                             new_order.customer_bill,
                             order_id]
                            )

            actual_order_id = order_id.getvalue()

            for item in new_order.cart_items:

                cursor.callproc('p_verify_product', [item.product_id])
                product_verify = cursor.getimplicitresults()
                product_row = product_verify[0].fetchone() if product_verify else None

                if product_row:
                    cursor.callproc('p_add_order_item',
                                    [actual_order_id,
                                     item.product_id,
                                     item.quantity])
                else:
                    db.rollback()
                    raise HTTPException(status_code=404, detail=f'Product Id {item.product_id} Not Exists!')

            return {
                'order_id' : actual_order_id,
                'customer_name' : new_order.customer_name,
                'customer_bill' : new_order.customer_bill,
                'Item Quantity' : len(new_order.cart_items)
            }

    except oracledb.Error as e:
        print(f'Database Error: {e}')

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to process order. Please try again later.')


@router.get('/', response_model=list[OrderCustomerOut])
def display_orders(offset:int = 0, limit:int = 10, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:

            cursor.callproc('p_display_orders', ['CUSTOMER'.upper(), offset, limit])
            data = cursor.getimplicitresults()
            rows = data[0].fetchall() if data else []

            orders = []

            for row in rows:

                result = {

                    'customer_name': row[0],
                    'customer_number': row[1],
                    'customer_city': row[2],
                    'customer_address': row[3],
                    'customer_bill': row[4],
                    'order_date': row[5],
                    'order_id' : row[6],
                }

                orders.append(result)

        return orders

    except oracledb.Error as e:
        print(f'Error for fetching checkout data {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to load orders data. Please try again later.')


@router.get('/admin', response_model=list[OrderAdminOut])
def display_orders_admin(offset:int = 0, limit:int = 10, token : str = Depends(get_token), db= Depends(get_db)):

    try:
        with db.cursor() as cursor:

            cursor.callproc('p_display_orders', ['ADMIN'.upper(), offset, limit])
            data = cursor.getimplicitresults()
            rows = data[0].fetchall() if data else []

            orders = []

            for row in rows:
                result = {

                    'order_id': row[0],
                    'customer_name': row[1],
                    'customer_number': row[2],
                    'customer_city': row[3],
                    'customer_address': row[4],
                    'customer_bill': row[5],
                    'order_date': row[6],
                    'order_status' : row[7],
                    'review_token' : row[8],
                    'review_status': row[9],
                    'items' : json.loads(row[10])
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
        'order_id' : row[6],
                }

    return result


@router.delete('/{order_id}')
def delete_order(order_id : int, token : str = Depends(get_token), db = Depends(get_db)):

   try:
        with db.cursor() as cursor:

            cursor.callproc('p_verify_order', [order_id])
            feedback = cursor.getimplicitresults()
            actual_fb = feedback[0].fetchone() if feedback else None

            if actual_fb:
                cursor.callproc('p_delete_order', [order_id])

                return {
                    'message' : f'Order {order_id} Deleted Successfully!'
                }

            else:
                raise HTTPException(status_code=404, detail=f'Order {order_id} Not Exists!')


   except oracledb.Error as e:
       print('Database Error', e)
       raise HTTPException(status_code=500, detail='Error Occurred On Our Side!')


@router.patch('/{order_id}/status')
def upd_sts_gen_tok(order_id : int, new_status : OrderStatus, token : str = Depends(get_token), db = Depends(get_db)):

    try:
        with db.cursor() as cursor:
            cursor.callproc('p_verify_order', [order_id])
            feedback = cursor.getimplicitresults()
            actual_fb = feedback[0].fetchone() if feedback else None

            if actual_fb:
                cursor.callproc('p_update_order_status', [order_id, new_status])

                if new_status.value.upper() == 'DELIVERED':
                    new_token = str(uuid4())

                    cursor.callproc('p_add_review_token', [new_token, order_id])

                    return {'status': new_status,
                            'review_token': new_token}
                return {'status': new_status}

            else:
                raise HTTPException(status_code=404, detail=f'Order {order_id} Not Exists!')

    except oracledb.Error as e:
        print('Error For Updating Status', e)
        raise HTTPException(status_code=500, detail='Error Occurred On Our Side!')

@router.put('/{order_id}')
def edit_order(order_id : int, updated_order : OrderUpdateIn, token : str = Depends(get_token), db=Depends(get_db)):

    try:

        with db.cursor() as cursor:
            cursor.callproc('p_verify_order', [order_id])
            feedback = cursor.getimplicitresults()
            actual_fb = feedback[0].fetchone() if feedback else None

            if actual_fb:

                cursor.callproc('p_edit_order',
                                [
                                 order_id,
                                 updated_order.customer_name,
                                 updated_order.customer_number,
                                 updated_order.customer_city,
                                 updated_order.customer_address,
                                 ])

                return {

                    'customer_name': updated_order.customer_name,
                    'customer_number': updated_order.customer_number,
                    'customer_city': updated_order.customer_city,
                    'customer_address': updated_order.customer_address
                }

            else:
                raise HTTPException(status_code=404, detail=f'Product {order_id} Not Exists!')

    except oracledb.Error as e:
        print('Error For Updating Product', e)
        raise HTTPException(status_code=500, detail='Error Occurred On Our Side!')