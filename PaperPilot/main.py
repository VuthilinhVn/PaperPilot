from fastapi import FastAPI
from routers import papers, users, favourite, history, ai_chat
from fastapi.middleware.cors import CORSMiddleware

from utils.Exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"msg": "Hello World"}
#挂载路由
app.include_router(papers.router)
app.include_router(users.router)
app.include_router(favourite.router)
app.include_router(history.router)

app.include_router(ai_chat.router)