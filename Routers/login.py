import oracledb

import security
from database import get_db
from jose import jwt, JWTError
from models import ChangeCredentials
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from security import hash_pass, verify_pass, create_access_token


router = APIRouter(prefix='/login', tags=['LOGIN'])
get_token = OAuth2PasswordBearer(tokenUrl='/login')


@router.post('/')
def login(credentials: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):

    with db.cursor() as cursor:

        hashed_pass = cursor.var(str)
        p_status = cursor.var(str)

        cursor.callproc('p_display_credentials', [credentials.username, hashed_pass, p_status])
        result_status = p_status.getvalue()

        if result_status.upper() == 'NO USER':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='INCORRECT USERNAME OR PASSWORD!')

        verify_password = verify_pass(credentials.password, hashed_pass.getvalue())

        if not verify_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='INCORRECT USERNAME OR PASSWORD!')


        jw_token = create_access_token({'sub': credentials.username})
        return {'access_token': jw_token, 'token_type':'bearer'}


@router.get('/verify', status_code=status.HTTP_200_OK)
def verify_profile(token : str = Depends(get_token)):


    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail='Token Expired',
                                          headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms='HS256')
        username = payload.get('sub')

        if username is None:
            raise credentials_exception

        return {username: username}

    except JWTError as e:
        print('JWT Error, ', e)
        raise credentials_exception


@router.put('/change-password')
def change_credentials(data: ChangeCredentials, token: str = Depends(get_token), db = Depends(get_db)):

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail='Token Expired',
                                          headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_name = payload.get('sub')

        if user_name is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    try:

        with db.cursor() as cursor:

            hashed_pass = cursor.var(str)
            p_status = cursor.var(str)

            cursor.callproc('p_display_credentials', [user_name, hashed_pass, p_status])

            if p_status.getvalue() == 'NO USER'.upper():
                raise credentials_exception

            verify_password = verify_pass(data.old_password, hashed_pass.getvalue())

            if not verify_password:
                raise credentials_exception

            new_hash_pass = hash_pass(data.new_password)

            cursor.callproc('p_change_credentials', [hashed_pass.getvalue(), new_hash_pass])


        return {
            'message' : 'Password Changed Successfully'
        }

    except oracledb.Error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Error In Database!')