import oracledb
from fastapi import APIRouter, Depends, HTTPException, status
from models import InventoryIn, InventoryOut
from database import get_db


router = APIRouter(prefix='/inventory', tags=['INVENTORY'])

@router.post('/', status_code=status.HTTP_201_CREATED)
def add_inventory(new_product: InventoryIn, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            cursor.callproc('p_add_inventory', [new_product.product_name,
                                            new_product.product_description,
                                            new_product.product_wholesale,
                                            new_product.product_retail,
                                            new_product.product_image
                                             ])
        result = {
            'product_name' : new_product.product_name,
            'product_retail' : new_product.product_retail,
            'product_image' : new_product.product_image
        }

        return result

    except oracledb.Error as e:
        print(f'Error Regarding DataBase: {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to add inventory. Please try again later.')


@router.get('/', response_model=list[InventoryOut])
def display_inventory(db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            data = cursor.var(oracledb.CURSOR)

            cursor.callproc('p_display_inventory', [data])
            out_cursor = data.getvalue()
            rows = out_cursor.fetchall()

            out_cursor.close()

            orders = []

            for row in rows:

                result = {

                    'product_id': row[0],
                    'product_name': row[1],
                    'product_description': row[2],
                    'product_wholesale': row[3],
                    'product_retail': row[4],
                    'product_image': row[5]
                }

                orders.append(result)

        return orders

    except oracledb.Error as e:
        print(f'Error for fetching checkout data {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to load inventory data. Please try again later.')