from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.device_schemas import *
from app.api.dependencies import device_service, verify_access_token

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

@router.get("/masters")
async def list_masters(service: DeviceService = Depends(device_service), user_id: int = Depends(verify_access_token)):
    masters = service.list_masters()
    return [MasterResponse(mac=m.mac) for m in masters]

@router.get("/masters/{mac}/slaves")
async def list_slaves_by_master(mac: str, service: DeviceService = Depends(device_service), user_id: int = Depends(verify_access_token)):
    slaves = service.list_slaves_by_master(mac)
    return [SlaveResponse(mac=s.mac, master=s.master) for s in slaves]

@router.get("/slaves")
async def list_slaves(service: DeviceService = Depends(device_service), user_id: int = Depends(verify_access_token)):
    slaves = service.list_slaves()
    return [SlaveResponse(mac=s.mac, master=s.master) for s in slaves]

