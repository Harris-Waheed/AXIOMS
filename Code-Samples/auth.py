import os
from jose import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

env_file = load_dotenv()

pwd_context = CryptContext(schemes=['bcrypt'])
SECRET_KEY = os.getenv('MY_SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
TOKEN_TIME = os.getenv('TIME')


def create_access_token(data: dict):

    to_encode = data.copy()

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=TOKEN_TIME)
    to_encode.update({'exp': expire})

    generate_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return generate_jwt


def hash_pass(plain_pass: str):
    return pwd_context.hash(plain_pass)


def verify_pass(plain_pass, hashed_pass):
    return pwd_context.verify(plain_pass, hashed_pass)
