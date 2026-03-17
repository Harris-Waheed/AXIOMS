import oracledb
import os
from dotenv import load_dotenv

env_file = load_dotenv()

db_pool = oracledb.create_pool(
    user = os.environ.get('DB_USER'),
    password = os.environ.get('DB_PASSWORD'),
    dsn = 'localhost/XEPDB1',
    min = 2,
    max = 11,
    increment = 1
)


def get_db():

    connection = db_pool.acquire()

    try:
        print('Database Connected!')
        yield connection

    finally:
        if connection:
            connection.close()
