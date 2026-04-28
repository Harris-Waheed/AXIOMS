from fastapi import APIRouter, HTTPException, Depends, status
from database import get_db
from models import ReviewsIn, ReviewsCustomerOut, ReviewsAdminOut
import oracledb
from uuid import uuid4

router = APIRouter(prefix='/reviews', tags=['Reviews'])


@router.post('/{token}', status_code=status.HTTP_201_CREATED)
def add_review(new_review : ReviewsIn, token : str, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            cursor.callproc('p_verify_review_status', [token])
            feedback = cursor.getimplicitresults()
            actual_fb = feedback[0].fetchone() if feedback else None

            if actual_fb and actual_fb[0].upper() == 'PENDING':
                cursor.callproc('p_add_review', [
                                new_review.name,
                                new_review.stars,
                                new_review.description
                ])

                cursor.callproc('p_update_review_status', [token])

                result = {
                    'name': new_review.name,
                    'stars': new_review.stars,
                    'description': new_review.description
                }

                return result

            else:
                raise HTTPException(status_code=400,
                                    detail=f'Review for Token {token} Already Submitted!')

    except oracledb.Error as e:
        print('Error In Database: ', e)
        raise HTTPException(status_code=500, detail='Failed to add review. Please try again later.')


@router.get('/', response_model=list[ReviewsCustomerOut])
def display_reviews(limit: int= 6, offset: int= 0, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            cursor.callproc('p_display_reviews', [offset, limit, 'CUSTOMER'])
            data = cursor.getimplicitresults()
            rows = data[0].fetchall() if data else None

            result = []

            if rows:
                for row in rows:
                    review = {'name' : row[0],
                              'stars' : row[1],
                              'description' : row[2],
                              'review_date' : row[3]
                              }

                    result.append(review)

            return result

    except oracledb.Error as e:
        print('Error In Database: ', e)
        raise HTTPException(status_code=500, detail='Failed to display review. Please try again later.')


@router.get('/admin', response_model=list[ReviewsAdminOut])
def display_reviews_admin(limit: int, offset: int, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            cursor.callproc('p_display_reviews', [offset, limit, 'ADMIN'])
            data = cursor.getimplicitresults()
            rows = data[0].fetchall() if data else None

            result = []

            if rows:
                for row in rows:
                    review = {'review_id':row[0],
                              'name' : row[1],
                              'stars' : row[2],
                              'description' : row[3],
                              'review_date' : row[4],
                              'review_status' : row[5]
                              }

                    result.append(review)

            return result

    except oracledb.Error as e:
        print('Error In Database: ', e)
        raise HTTPException(status_code=500, detail='Failed to display review. Please try again later.')


@router.patch('/{order_id}/review_token') # Generated token for review form when delivered order is clicked by admin
def generate_token(order_id : int, db= Depends(get_db)):

    new_token = str(uuid4())

    try:
        with db.cursor() as cursor:

            cursor.callproc('p_verify_order', [order_id])
            feedback = cursor.getimplicitresults()
            actual_fb = feedback[0].fetchone() if feedback else None

            if actual_fb:
                cursor.callproc('p_add_review_token', [new_token, order_id])

                return {
                    "message": "Token successfully generated and saved.",
                }

            else:
                raise HTTPException(status_code=404, detail=f'Order {order_id} Not Exists!')

    except oracledb.Error as e:
        print('Error In Database: ', e)
        raise HTTPException(status_code=500, detail='Failed to add review token. Please try again later.')

@router.patch('/{review_id}/status')
def update_review_visibility(review_id : int, new_status : str, db = Depends(get_db)):

    try:
        with db.cursor() as cursor:

            cursor.callproc('p_update_review_visibility', [review_id, new_status.upper()])
            return {'status': new_status}

    except oracledb.Error as e:
        print('Error For Updating Review Status', e)
        raise HTTPException(status_code=500, detail='Error Occurred On Our Side!')

@router.delete('/{review_id}')
def delete_review(review_id: int, db=Depends(get_db)):

    try:
        with db.cursor() as cursor:
            cursor.callproc('p_delete_review', [review_id])

            return {
                'message' : 'Review Deleted Successfully'
            }

    except oracledb.Error as e:
        print('Error For Deleting Review', e)
        raise HTTPException(status_code=500, detail='Error Occurred On Our Side!')
