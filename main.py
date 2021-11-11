from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

CONNECTION_STRING = "mongodb://localhost"
try:
    client = MongoClient(CONNECTION_STRING, serverSelectionTimeoutMS=3000)
    print('Connected ! Mongo version is', client.server_info()['version'])
except:
    print('Disconnected !')

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

templates = Jinja2Templates(directory="static")

@app.get("/")
async def root():
    db = get_database()
    c = db['key'].find({"_id":2})
    if (c):
        return {"message": c[0]}
    return {"message": c}

@app.get("/get/{id}")
async def root(id: int):
    db = get_database()
    c = list(db['key'].find({"_id":id}))
    return {"message": c}

@app.get("/delete/{id}")
async def root(id: int):
    db = get_database()
    our_filter = { 'competitionId': { '$in': ["30629", 30630] } }
    our_hint = [('competitionId', 1)]
    c = db['key'].delete_many(filter = our_filter,hint = our_hint)
    return {"message": c.deleted_count}

@app.get("/items/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Some HTML in here</title> 
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("page.html", {"request": request, "id": id})

class Book(BaseModel):
    title: str
    size: int

@app.post("/books/")
async def create_item(book: Book):
    return book

def get_database():
    return client['test']
    
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":    
    print('__main__ !')
    # Get the database
    dbname = get_database()