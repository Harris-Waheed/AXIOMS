from fastapi import FastAPI
from Routers import checkout, inventory
import uvicorn

app = FastAPI()

app.include_router(checkout.router)
app.include_router(inventory.router)


if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000)