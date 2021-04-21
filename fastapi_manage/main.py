# app.py
from fastapi import FastAPI,Response,Request
from fastapi.responses import HTMLResponse,RedirectResponse
from pydantic import BaseModel
from typing import Optional, Text
from datetime import datetime
from rsa_company_gen import encode_rsa,generate_licensefile
from fastapi.templating import Jinja2Templates
app = FastAPI()

codedb = []
templates = Jinja2Templates(directory="templates")
# post model
class Code(BaseModel):
    #id: int
    user: str
    code: Optional[str]=False
    expired: str
    mac_address:str

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



@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})