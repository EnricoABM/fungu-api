from sqlalchemy.orm import Session

from app.models.device import Master, Slave 

class DeviceRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def save_master(self, master: Master):
        self.session.add(master)
        self.session.commit()

    def find_master_by_mac(self, mac: str):
        return self.session.query(Master).filter(Master.mac == mac).first()

    def save_slave(self, slave: Slave):
        self.session.add(slave)
        self.session.commit()

    def find_slave_by_mac(self, mac: str):
        return self.session.query(Slave).filter(Slave.mac == mac).first()

    def find_slaves_by_master_mac(self, mac: str):
        return self.session.query(Slave).filter(Slave.master == mac).all()

    def find_all_masters(self):
        return self.session.query(Master).all()

    def find_all_slaves(self):
        return self.session.query(Slave).all()