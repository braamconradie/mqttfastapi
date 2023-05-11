from fastapi import FastAPI
import uvicorn
#from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

print("Alive")

#test

origins = [
    "http://localhost.tiangolo.com",
     "https://api-cors-tester-client-side.glitch.me/"
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def main():
    return {"hello": "world"}
  
@app.get("/hello")
async def main():
    return {"hello": "slimkop"}
  
  
@app.get("/items/{item}")
async def subpage(item: str):
    return {"item": item}

  
  
uvicorn.run(app, port = 8080, host = "0.0.0.0")