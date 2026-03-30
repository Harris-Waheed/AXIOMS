import oracledb
from fastapi import APIRouter, Depends, HTTPException, status
from models import InventoryIn, InventoryCustomerOut, InventoryAdminOut, ProductStatus
from database import get_db


router = APIRouter(prefix='/inventory', tags=['INVENTORY'])

@router.post('/', status_code=status.HTTP_201_CREATED)
def add_inventory(new_product: InventoryIn, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            product_link = str(new_product.product_link) if new_product.product_link else None

            cursor.callproc('p_add_inventory', [new_product.product_name,
                                            new_product.product_description,
                                            new_product.product_wholesale,
                                            new_product.product_retail,
                                            new_product.product_image,
                                            new_product.product_category,
                                            product_link
                                             ])
        result = {
            'product_name' : new_product.product_name,
            'product_retail' : new_product.product_retail,
            'product_image' : new_product.product_image,
            'product_category' : new_product.product_category,
            'product_link' : new_product.product_link
        }

        return result

    except oracledb.Error as e:
        print(f'Error Regarding DataBase: {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to add inventory. Please try again later.')


@router.get('/', response_model=list[InventoryCustomerOut])
def display_customer_inventory(db= Depends(get_db)):

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
                    'product_retail': row[4],
                    'product_image': row[5],
                    'product_category' : row[7]
                }

                orders.append(result)

        return orders

    except oracledb.Error as e:
        print(f'Error for fetching checkout data {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to load inventory data. Please try again later.')

@router.get('/admin', response_model=list[InventoryAdminOut])
def display_admin_inventory(db= Depends(get_db)):

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
                    'product_image': row[5],
                    'product_link': row[6],
                    'product_category' : row[7],
                    'product_status': row[8]
                }

                orders.append(result)

        return orders

    except oracledb.Error as e:
        print(f'Error for fetching checkout data {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to load inventory data. Please try again later.')

@router.get('/{item_id}', response_model=InventoryCustomerOut)
def display_product(item_id: int, db=Depends(get_db)):

    try:
        with db.cursor() as cursor:

            cursor.callproc('p_display_product', [item_id])
            results = cursor.getimplicitresults()

            if results:
                row = results[0].fetchone()
            else:
                row = None

    except oracledb.Error as e:
        print(f'Database Error: {e}')
        raise HTTPException(status_code=500, detail='Unable to load!')

    if not row:
        raise HTTPException(status_code=404, detail='Product Not Found!')

    result = {
        'product_id': row[0],
        'product_name': row[1],
        'product_description': row[2],
        'product_retail': row[4],
        'product_image': row[5],
        'product_category' : row[7]
    }

    return result

@router.delete('/{product_id}')
def delete_product(product_id : int, db = Depends(get_db)):

   try:
        with db.cursor() as cursor:

            cursor.callproc('p_verify_product', [product_id])
            feedback = cursor.getimplicitresults()
            actual_fb = feedback[0].fetchone() if feedback else None

            if actual_fb:
                cursor.callproc('p_delete_product', [product_id])

                return {
                    'message' : f'Product {product_id} Deleted Successfully!'
                }

            else:
                raise HTTPException(status_code=404, detail=f'Product {product_id} Not Exists!')


   except oracledb.Error as e:
       print('Database Error', e)
       raise HTTPException(status_code=500, detail='Error Occurred On Our Side!')

@router.put('/{product_id}')
def update_product_status(product_id : int, new_status : ProductStatus, db = Depends(get_db)):

    try:
        with db.cursor() as cursor:
            cursor.callproc('p_verify_product', [product_id])
            feedback = cursor.getimplicitresults()
            actual_fb = feedback[0].fetchone() if feedback else None

            if actual_fb:

                cursor.callproc('p_update_product_status', [product_id, new_status])
                return {'status': new_status}

            else:
                raise HTTPException(status_code=404, detail=f'Product {product_id} Not Exists!')

    except oracledb.Error as e:
        print('Error For Updating Status', e)
        raise HTTPException(status_code=500, detail='Error Occurred On Our Side!')
