from pydantic import BaseModel

class MasterRegisterSchema(BaseModel):
    mac: str

class SlaveRegisterSchema(BaseModel):
    mac_master: str
    mac_slave: str

class MeasurementRegister(BaseModel):
    mac_master: str
    mac_slave: str
    temp: str
    hum: str
    co2: str
    tvoc: str 
    aqi: str 
    lux: str
