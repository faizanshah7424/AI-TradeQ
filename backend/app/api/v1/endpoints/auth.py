from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def auth_status():
    return {
        "status": "Authentication foundation active",
        "methods": ["JWT", "RBAC"],
        "notice": "Login business logic not implemented in bootstrap task."
    }
