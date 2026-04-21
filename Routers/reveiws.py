from fastapi import APIRouter, HTTPException, Depends, status
from database import get_db
from models import Reviews
import oracledb

router = APIRouter(prefix='/reviews', tags=['Reviews'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def add_review(new_review : Reviews, db= Depends(get_db)):

    try:
        with db.cursor() as cursor:
            cursor.callproc('p_add_review', [
                            new_review.name,
                            new_review.stars,
                            new_review.description
            ])

        result = {
            'name': new_review.name,
            'stars': new_review.stars,
            'description': new_review.description
        }

        return result

    except oracledb.Error as e:
        print('Error In Database: ', e)
        raise HTTPException(status_code=500, detail='Failed to add review. Please try again later.')


