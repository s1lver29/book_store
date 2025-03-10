from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.routers import v1_router

app = FastAPI(
    title="Book Library App",
    description="Учебное приложение для MTS Shad",
    version="0.0.1",
    default_response_class=ORJSONResponse,
    responses={404: {"description": "Not found!"}},
)


app.include_router(v1_router)
