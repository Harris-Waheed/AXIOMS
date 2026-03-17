import oracledb
import os
from dotenv import load_dotenv

env_file = load_dotenv()

USER = os.environ.get('USER')
PASSWORD = os.environ.get('PASSWORD')
DSN = 'localhost/XEPDB1'


def get_db():

    connection = None

    try:
        connection = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
        print('Database Connected!')
        yield connection

    finally:
        if connection:
            connection.close()
