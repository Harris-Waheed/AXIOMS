from fastapi import FastAPI
from Routers import checkout, inventory, reviews, login
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://axioms-pk.me",
    "https://www.axioms-pk.me"
]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_headers=['*'],
                   allow_credentials=False,
                   allow_methods=['*'],
                   )

app.include_router(login.router)
app.include_router(checkout.router)
app.include_router(inventory.router)
app.include_router(reviews.router)


if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000)
