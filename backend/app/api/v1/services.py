from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/services", status_code=501)
async def services() -> None:
    raise HTTPException(status_code=501, detail="Government services are not implemented yet")
