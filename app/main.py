# TechScale - API Application
# This file is already complete. Do not modify it.

from fastapi import FastAPI
from pydantic import BaseModel
from order_routes import router as order_router

app = FastAPI(title="TechScale API", version="1.0.0")
app.include_router(order_router)


class HealthResponse(BaseModel):
    status: str
    version: str


class ProcessRequest(BaseModel):
    user_id: int
    action: str


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/process", status_code=202)
def process_request(request: ProcessRequest):
    return {
        "message": f"Processing action {request.action} for user {request.user_id}"
    }
