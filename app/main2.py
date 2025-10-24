# from fastapi import FastAPI, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from auth import get_user
#
# import logging
# import uvicorn
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("alerter:server")
#
# app = FastAPI(title="ServiceAlerting")
#
#
# @app.get("/")
# async def home(current_user: dict = Depends(get_user)):
#     return {"message": f"Hello, {current_user['username']}!"}
#
#
# @app.post("/login")
# async def login():
#     return {}
#
#
# @app.post("/register")
# async def register():
#     return {}
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )
#
# if __name__ == "__main__":
#     uvicorn.run("main:app", port=5252, reload=True)
