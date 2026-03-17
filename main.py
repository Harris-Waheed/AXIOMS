from fastapi import FastAPI
from Routers import checkout
import uvicorn

app = FastAPI()

app.include_router(checkout.router)



if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000)