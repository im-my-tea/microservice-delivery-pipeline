from fastapi import FastAPI
from pydantic import BaseModel

class ServerMetric(BaseModel):
    server_name: str
    cpu_usage: float
    ram_usage: int
    is_active: bool


app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "running", "version": "1.0.0"}

@app.post("/metrics")
def ingest_metrics(data: ServerMetric):
    print(f"Received metrics from: {data.server_name}! CPU Usage: {data.cpu_usage}")
    return {"message": "Data Received", "server": data.server_name}