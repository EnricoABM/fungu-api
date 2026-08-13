from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.device_schemas import *
from app.api.dependencies import device_service

from app.services.device_service import DeviceService

router = APIRouter()

@router.post("/master/register")
async def newMaster(schema: MasterRegisterSchema, service: DeviceService = Depends(device_service)):
    try:
        service.register_master(schema.mac)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register")
async def newSlayer(schema: SlaveRegisterSchema, service: DeviceService = Depends(device_service)):
    try:
        service.register_slave(schema.mac_master, schema.mac_slave)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

