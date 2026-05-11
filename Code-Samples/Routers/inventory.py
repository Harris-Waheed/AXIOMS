import oracledb
from database import get_db
from Routers.login import get_token
from fastapi import APIRouter, Depends, HTTPException, status
from models import InventoryIn, InventoryCustomerOut, ProductStatus


router = APIRouter(prefix='/inventory', tags=['INVENTORY'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def add_inventory(new_product: InventoryIn, token : str = Depends(get_token), db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            product_link = str(new_product.product_link) if new_product.product_link else None
            product_id = cursor.var(int)

            cursor.callproc('p_add_inventory', [
                                            product_id,
                                            new_product.product_name,
                                            new_product.product_description,
                                            new_product.product_wholesale,
                                            new_product.product_retail,
                                            new_product.product_image,
                                            product_link,
                                            new_product.product_category
                                             ])
        return {
            'product_id' : product_id.getvalue(),
            'product_name' : new_product.product_name,
            'product_retail' : new_product.product_retail,
            'product_image' : new_product.product_image,
            'product_category' : new_product.product_category,
            'product_link' : new_product.product_link
        }

    except oracledb.Error as e:
        print(f'Error Regarding DataBase: {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to add inventory. Please try again later.')


@router.get('/', response_model=list[InventoryCustomerOut])
def display_customer_inventory(db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            data = cursor.var(oracledb.CURSOR)

            cursor.callproc('p_display_inventory', [data, 'CUSTOMER'.upper()])
            out_cursor = data.getvalue()
            rows = out_cursor.fetchall()

            out_cursor.close()

            inventory_list = []

            for row in rows:

                result = {

                    'product_id': row[0],
                    'product_name': row[1],
                    'product_description': row[2],
                    'product_retail': row[3],
                    'product_image': row[4],
                    'product_category' : row[5]
                }

                inventory_list.append(result)

        return inventory_list

    except oracledb.Error as e:
        print(f'Error for fetching checkout data {e}')

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Failed to load inventory data. Please try again later.')


@router.patch('/{product_id}/status')
def update_product_status(product_id : int, new_status : ProductStatus, token : str = Depends(get_token),
                                                                                                db = Depends(get_db)):

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
