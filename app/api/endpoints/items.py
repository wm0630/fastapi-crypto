from fastapi import APIRouter, HTTPException


router = APIRouter()

@router.get("/{item_id}")
async def read_item(item_id: int):
    return item_id

@router.get("/")
async def read_items():
    return "Hello world!"
