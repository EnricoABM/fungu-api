from sqlalchemy.orm import Session

from app.models.device import Master, Slave
from app.repository.device_repository import DeviceRepository


class DeviceService:
    repository: DeviceRepository

    def __init__(self, session: Session):
        self.repository = DeviceRepository(session)

    def register_master(self, mac: str):
        device = self.find_master_by_mac(mac)
        if device:
            raise ValueError("Mestre já cadastrado")

        new_device = Master(mac)
        self.repository.save_master(new_device)

    def find_master_by_mac(self, mac: str):
        return self.repository.find_master_by_mac(mac)

    def register_slave(self, master: str, slave: str):
        slave_dev = self.find_slave_by_mac(slave)
        if slave_dev:
            raise ValueError("Dispositivo já cadastrado")

        master_dev = self.find_master_by_mac(master)
        if not master_dev:
            raise ValueError("Mestre não cadastrado")
        
        new_device = Slave(slave, master)
        self.repository.save_slave(new_device)

    def find_slave_by_mac(self, mac: str):
        return self.repository.find_slave_by_mac(mac)

    def find_slaves_by_mac_master(self, mac: str):
        return self.repository.find_slaves_by_master_mac(mac)
        