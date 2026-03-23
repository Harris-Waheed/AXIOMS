from fastapi import FastAPI
from Routers import checkout, inventory
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=['*'],
                   allow_headers=['*'],
                   allow_credentials=True,
                   allow_methods=['*'],
                   )

app.include_router(checkout.router)
app.include_router(inventory.router)


if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000)