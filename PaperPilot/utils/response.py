from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response(message:str="success", data=None):
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    #把任何的数据转换为json
    return JSONResponse(content =jsonable_encoder(content))

def fail_response(code:int, msg:str):
    content = {
        "code": code,
        "message": msg,
        "data": None
    }
    return JSONResponse(content =jsonable_encoder(content))



