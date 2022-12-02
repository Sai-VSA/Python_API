from fastapi import FastAPI, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import posts, users, auth, votes

app = FastAPI()

origins = []

app.add_middleware(
     CORSMiddleware,
     allow_origins = origins,
     allow_credentials = [],
     allow_methods=["*"],
     allow_headers=["*"]
)

## Path Operation
@app.get("/") # Decorator allows someone to reach these functions using fastAPI (@)
# HTTP get request response to root path "/" of host website (base URL)
async def root(): ## function with arbitrary name, it helps to be as descriptive as possible
     return{"message": "Hello Worlds"} ## fastAPI converts this to JSON format

app.include_router(posts.router) ## go down the list of routers when getting HTTP requests
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)
