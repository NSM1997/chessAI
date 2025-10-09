from fastapi import APIRouter

router = APIRouter()

# Example endpoint
@router.get("/example")
async def example():
    return {"message": "This is an example endpoint"}