# app.py
from fastapi import FastAPI,Response,Request,Form,Depends
from fastapi.responses import HTMLResponse,RedirectResponse
from pydantic import BaseModel,Field
from typing import Optional, Text,List
from datetime import datetime
from rsa_company_gen import encode_rsa,generate_licensefile
from fastapi.templating import Jinja2Templates
import sqlalchemy
import databases

DATABASE_URL = "sqlite:///./test.db"

metadata = sqlalchemy.MetaData()

database=databases.Database(DATABASE_URL)
notes=sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id",sqlalchemy.Integer,primary_key=True),
    sqlalchemy.Column("user",sqlalchemy.String(500)),
    sqlalchemy.Column("code",sqlalchemy.String(500)),
    sqlalchemy.Column("expired",sqlalchemy.String(500)),
    sqlalchemy.Column("mac_address",sqlalchemy.String(500)),

)
engine=sqlalchemy.create_engine(
    DATABASE_URL,connect_args={"check_same_thread":False}
)
metadata.create_all(engine)

app = FastAPI()



codedb = []

class CodeIn(BaseModel):
    user: str
    code: Optional[str]=False
    expired: str
    mac_address:str
# post model
class Code(BaseModel):
    id: int
    user: str
    code: Optional[str]=False
    expired: str
    mac_address:str

@app.on_event("startup")
async def connect():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post('/register',response_model=Code)
async def create(code:CodeIn):
    code_arg = code.expired
    code_arg+= code.mac_address
    encode=encode_rsa(code_arg,code.mac_address)
    code.code=encode
    query=notes.insert().values(
        user=code.user,
        expired=code.expired,
        code=encode,
        mac_address=code.mac_address
    )
    record_id=await database.execute(query)

    return {**code.dict(),"id":record_id}

@app.get("/register/", response_model=List[Code])
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)

@app.get('/register/{code_id}',response_model=Code)
async def get_one(code_id:int):
    print(code_id)
    print(notes.c.id==code_id)
    query=notes.select().where(notes.c.id==code_id)
    #query = "SELECT * FROM notes WHERE ID={}".format(str(code_id))
    print(query)
    row=await database.fetch_one(query)
    return row

@app.put('/register/{code_id}',response_model=Code,response_model_include={"id", "user","code","expired","mac_address"})
async def update(code_id:int ,r: CodeIn=Depends()):
    code_arg = r.expired
    code_arg+= r.mac_address
    encode=encode_rsa(code_arg,r.mac_address)
    
    query=notes.update().where(notes.c.id==code_id).values(
        user=r.user,
        expired=r.expired,
        code=encode,
        mac_address=r.mac_address
    )
    print(query)
    record_id= await database.execute(query)
    print(record_id)
    query=notes.select().where(notes.c.id == record_id)
    user=await database.fetch_one(query)
    return user

@app.delete("/register/{code_id}",response_model=Code)
async def delete(code_id:int):
    query=notes.delete().where(notes.c.id == code_id)
    return await database.execute(query)

@app.get("/")
def read_root():
  return {"home": "Home page"}

@app.get("/code")
def get_posts():
    return codedb
# ADD
@app.post("/code")
def add_post(code: Code):
    code_arg = code.expired
    code_arg+= code.mac_address
    encode=encode_rsa(code_arg,code.mac_address)
    code.code=encode
    #generate_licensefile(encode)
    codedb.append(code.dict())
    return codedb[-1]

@app.get("/code/{code_id}")
def get_post(code_id: int):
    code = code_id - 1
    return codedb[code]

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})

# Update
@app.post("/code/{code_id}")
def update_post(code_id: int, code: Code):
    
    code.user=codedb[code_id]['user']
    date= code.expired
    machine_code= code.mac_address

    code_arg = date
    code_arg+= machine_code
    encode=encode_rsa(code_arg,code.mac_address)
    code.code=encode
    #generate_licensefile(encode)
    code.mac_address=codedb[code_id]['mac_address']
    codedb[code_id] = code
    
    return {"message": "Code has been updated succesfully"}


# Delete
@app.delete("/code/{code_id}")
def delete_post(code_id: int):
    codedb.pop(code_id-1)
    return {"message": "Post has been deleted succesfully"}



@app.get("/items/")
async def read_items():
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/legacy/")
def get_legacy_data():
    data = """<?xml version="1.0"?>
    <shampoo>
    <Header>
        Apply shampoo here.
    </Header>
    <Body>
        You'll have to use soap here.
    </Body>
    </shampoo>
    """
    return Response(content=data, media_type="application/xml")


templates = Jinja2Templates(directory="templates")

@app.get('/download')
def form_post(request: Request):
    result = 'Type a number'
    
    return templates.TemplateResponse('/item.html', context={'request': request, 'result': result})

@app.get('/test', response_class=HTMLResponse)
def form_post(request: Request):
    result = 'Type a number'
    
    return templates.TemplateResponse('/item.html', context={'request': request, 'result': result})