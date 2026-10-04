"""FastAPI Containerized Microservice for AWS Deployment."""
import os
import platform
import socket
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from app.models import HealthResponse, ItemCreate, ItemResponse, SystemInfoResponse

# Record service start time
START_TIME = time.time()
SERVICE_NAME = "cloud-assessment-microservice"
SERVICE_VERSION = "1.0.0"

app = FastAPI(
    title="AWS Containerized Microservice",
    description="A lightweight, production-ready microservice built for containerized deployment on AWS (ECR + EC2/ECS).",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for cross-origin client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demonstration purposes
# Seed with initial items
ITEMS_DB: Dict[int, dict] = {
    1: {
        "id": 1,
        "title": "Set up AWS ECR repository",
        "description": "Create elastic container registry repository for docker image storage.",
        "status": "completed",
        "priority": "high",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    2: {
        "id": 2,
        "title": "Launch EC2 container host",
        "description": "Launch EC2 instance with Docker engine installed.",
        "status": "in_progress",
        "priority": "high",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
    3: {
        "id": 3,
        "title": "Configure GitHub Actions CI/CD",
        "description": "Automate test execution, container build, and deployment.",
        "status": "pending",
        "priority": "normal",
        "created_at": datetime.now(timezone.utc).isoformat(),
    },
}
ID_COUNTER = 3


@app.get("/", summary="Root Endpoint")
def read_root():
    """Welcome endpoint providing service identity and navigation links."""
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "message": "Welcome to the AWS Containerized Microservice!",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "health": "GET /health",
            "system_info": "GET /api/info",
            "list_items": "GET /api/items",
            "create_item": "POST /api/items",
            "get_item": "GET /api/items/{id}",
            "delete_item": "DELETE /api/items/{id}",
        },
    }


@app.get("/health", response_model=HealthResponse, summary="Health Check")
def health_check():
    """Target group / load balancer health check endpoint."""
    uptime = time.time() - START_TIME
    return HealthResponse(
        status="healthy",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        uptime_seconds=round(uptime, 2),
    )


@app.get("/api/info", response_model=SystemInfoResponse, summary="Container & System Information")
def system_info():
    """Returns runtime host/container information to demonstrate containerized isolation."""
    return SystemInfoResponse(
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        hostname=socket.gethostname(),
        platform=platform.platform(),
        python_version=platform.python_version(),
        environment=os.getenv("APP_ENV", "production"),
    )


@app.get("/api/items", response_model=List[ItemResponse], summary="List Items")
def list_items(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g. pending, completed)"),
    limit: int = Query(50, ge=1, le=100, description="Max number of items to return"),
):
    """Retrieve all stored items, optionally filtered by status."""
    items = list(ITEMS_DB.values())
    if status_filter:
        items = [item for item in items if item["status"].lower() == status_filter.lower()]
    return items[:limit]


@app.get("/api/items/{item_id}", response_model=ItemResponse, summary="Get Item by ID")
def get_item(item_id: int):
    """Retrieve a single item by its ID."""
    if item_id not in ITEMS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return ITEMS_DB[item_id]


@app.post("/api/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="Create Item")
def create_item(payload: ItemCreate):
    """Create a new item in the database."""
    global ID_COUNTER
    ID_COUNTER += 1
    new_item = {
        "id": ID_COUNTER,
        "title": payload.title,
        "description": payload.description,
        "status": payload.status,
        "priority": payload.priority,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ITEMS_DB[ID_COUNTER] = new_item
    return new_item


@app.delete("/api/items/{item_id}", status_code=status.HTTP_200_OK, summary="Delete Item")
def delete_item(item_id: int):
    """Delete an item by its ID."""
    if item_id not in ITEMS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    deleted = ITEMS_DB.pop(item_id)
    return {"message": f"Item {item_id} deleted successfully", "deleted_item": deleted}
