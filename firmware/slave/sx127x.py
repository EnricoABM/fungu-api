import time

class SX127x:
    # Registradores do SX1276
    REG_FIFO = 0x00
    REG_OP_MODE = 0x01
    REG_FRF_MSB = 0x06
    REG_FRF_MID = 0x07
    REG_FRF_LSB = 0x08
    REG_PA_CONFIG = 0x09
    REG_FIFO_ADDR_PTR = 0x0D
    REG_FIFO_TX_BASE_ADDR = 0x0E
    REG_FIFO_RX_BASE_ADDR = 0x0F
    REG_FIFO_RX_CURRENT_ADDR = 0x10
    REG_IRQ_FLAGS = 0x12
    REG_RX_NB_BYTES = 0x13
    REG_MODEM_CONFIG_1 = 0x1D
    REG_MODEM_CONFIG_2 = 0x1E
    REG_PAYLOAD_LENGTH = 0x22

    # Modos de operação
    MODE_SLEEP = 0x00
    MODE_STDBY = 0x01
    MODE_TX = 0x03
    MODE_RXCONT = 0x05
    LONG_RANGE_MODE = 0x80

    # Máscaras de interrupção (IRQ)
    IRQ_TX_DONE_MASK = 0x08
    IRQ_PAYLOAD_CRC_ERROR_MASK = 0x20
    IRQ_RX_DONE_MASK = 0x40

    def __init__(self, spi, pins, parameters):
        self.spi = spi
        self.cs = pins['cs']
        self.reset = pins.get('reset')
        
        self.cs.init(self.cs.OUT, value=1)

        # Sequência de Reset do módulo
        if self.reset:
            self.reset.init(self.reset.OUT, value=0)
            time.sleep(0.01)
            self.reset.value(1)
            time.sleep(0.01)

        self.sleep()
        self.set_frequency(parameters.get('frequency', 915E6))
        self.set_tx_power(parameters.get('tx_power_level', 14))
        self.set_bandwidth(parameters.get('signal_bandwidth', 125E3))
        self.set_spreading_factor(parameters.get('spreading_factor', 8))
        self.set_coding_rate(parameters.get('coding_rate', 5))
        
        # Define os endereços base de RX e TX para 0 na FIFO
        self.write_register(self.REG_FIFO_RX_BASE_ADDR, 0)
        self.write_register(self.REG_FIFO_TX_BASE_ADDR, 0)
        
        self.standby()

    def read_register(self, addr):
        self.cs.value(0)
        self.spi.write(bytearray([addr & 0x7F]))
        res = self.spi.read(1)
        self.cs.value(1)
        return res[0]

    def write_register(self, addr, value):
        self.cs.value(0)
        self.spi.write(bytearray([addr | 0x80, value]))
        self.cs.value(1)

    def sleep(self):
        self.write_register(self.REG_OP_MODE, self.LONG_RANGE_MODE | self.MODE_SLEEP)

    def standby(self):
        self.write_register(self.REG_OP_MODE, self.LONG_RANGE_MODE | self.MODE_STDBY)

    def set_frequency(self, freq):
        frf = int((freq << 19) / 32000000)
        self.write_register(self.REG_FRF_MSB, (frf >> 16) & 0xFF)
        self.write_register(self.REG_FRF_MID, (frf >> 8) & 0xFF)
        self.write_register(self.REG_FRF_LSB, (frf >> 0) & 0xFF)

    def set_tx_power(self, level):
        if level > 17: level = 17
        if level < 2: level = 2
        self.write_register(self.REG_PA_CONFIG, 0x80 | (level - 2))

    def set_bandwidth(self, bw):
        bw_bins = (7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3, 250E3, 500E3)
        bw_id = 7 # Padrão 125 kHz
        for i, b in enumerate(bw_bins):
            if bw <= b:
                bw_id = i
                break
        val = self.read_register(self.REG_MODEM_CONFIG_1)
        self.write_register(self.REG_MODEM_CONFIG_1, (val & 0x0F) | (bw_id << 4))

    def set_spreading_factor(self, sf):
        if sf < 6: sf = 6
        if sf > 12: sf = 12
        val = self.read_register(self.REG_MODEM_CONFIG_2)
        self.write_register(self.REG_MODEM_CONFIG_2, (val & 0x0F) | (sf << 4))

    def set_coding_rate(self, cr):
        den = cr - 4
        if den < 1: den = 1
        if den > 4: den = 4
        val = self.read_register(self.REG_MODEM_CONFIG_1)
        self.write_register(self.REG_MODEM_CONFIG_1, (val & 0xF1) | (den << 1))

    # ==========================================
    # FUNÇÕES DE TRANSMISSÃO (TX)
    # ==========================================
    def println(self, string):
        """Envia uma string e adiciona quebra de linha"""
        self.write(string.encode('utf-8') + b'\n')

    def write(self, payload):
        """Transmite o payload bruto (bytes)"""
        self.standby()
        
        self.write_register(self.REG_FIFO_ADDR_PTR, self.read_register(self.REG_FIFO_TX_BASE_ADDR))
        self.write_register(self.REG_PAYLOAD_LENGTH, len(payload))
        
        self.cs.value(0)
        self.spi.write(bytearray([self.REG_FIFO | 0x80]))
        self.spi.write(payload)
        self.cs.value(1)
        
        self.write_register(self.REG_OP_MODE, self.LONG_RANGE_MODE | self.MODE_TX)
        
        timeout_tx = time.ticks_ms() + 2000
        sucesso = True
        
        while (self.read_register(self.REG_IRQ_FLAGS) & self.IRQ_TX_DONE_MASK) == 0:
            if time.ticks_ms() > timeout_tx:
                sucesso = False
                break
            time.sleep(0.01)
        
        self.write_register(self.REG_IRQ_FLAGS, self.IRQ_TX_DONE_MASK)
        
        if not sucesso:
            raise Exception("Timeout na transmissao LoRa")

    # ==========================================
    # FUNÇÕES DE RECEPÇÃO (RX)
    # ==========================================
    def receive(self):
        """Coloca o módulo em modo de recepção contínua"""
        self.standby()
        self.write_register(self.REG_OP_MODE, self.LONG_RANGE_MODE | self.MODE_RXCONT)

    def check_msg(self):
        """Verifica se um pacote chegou e checa integridade (CRC)"""
        irq_flags = self.read_register(self.REG_IRQ_FLAGS)
        
        # Limpa todas as flags de interrupção
        self.write_register(self.REG_IRQ_FLAGS, irq_flags)
        
        if (irq_flags & self.IRQ_RX_DONE_MASK) == 0:
            return False
            
        if (irq_flags & self.IRQ_PAYLOAD_CRC_ERROR_MASK) != 0:
            # Pacote corrompido ou ruído fantasma
            return False
            
        return True

    def read_payload(self):
        """Lê os bytes da FIFO recebidos via rádio"""
        current_addr = self.read_register(self.REG_FIFO_RX_CURRENT_ADDR)
        packet_length = self.read_register(self.REG_RX_NB_BYTES)
        
        self.write_register(self.REG_FIFO_ADDR_PTR, current_addr)
        
        self.cs.value(0)
        self.spi.write(bytearray([self.REG_FIFO & 0x7F]))
        payload = self.spi.read(packet_length)
        self.cs.value(1)
        
        return payload
