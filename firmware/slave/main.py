from machine import Pin, I2C
import ssd1306
import ens160
from aht21 import AHT21
from bh1750 import BH1750
import time
import network
import socket
import json
import ubinascii

# ==========================================
# HARDWARE E DISPLAY
# ==========================================
oled_reset = Pin(16, Pin.OUT)
oled_reset.value(0)
time.sleep(0.1)
oled_reset.value(1)

# I2C Sensores atualizado conforme mapeamento (SDA=22, SCL=21)
i2c_sensores = I2C(0, scl=Pin(21), sda=Pin(22), freq=100000)
i2c_display = I2C(1, scl=Pin(15), sda=Pin(4), freq=100000)

oled = ssd1306.SSD1306_I2C(128, 64, i2c_display)
oled.fill(0)
oled.text("Iniciando...", 0, 0)
oled.show()

print("Dispositivos I2C Sensores:", i2c_sensores.scan())

# ==========================================
# INICIALIZAÇÃO DOS SENSORES
# ==========================================
climate, air, light = None, None, None

try:
    climate = AHT21(i2c_sensores)
    print("[OK] AHT21 Ativo")
except Exception as e:
    print("[ERRO] AHT21:", e)

try:
    air = ens160.ENS160(i2c_sensores)
    print("[OK] ENS160 Ativo (Modo Standard)")
except Exception as e:
    print("[ERRO] ENS160:", e)

try:
    light = BH1750(i2c_sensores)
    print("[OK] BH1750 Ativo")
except Exception as e:
    print("[ERRO] BH1750:", e)

# ==========================================
# REDE E SOCKET
# ==========================================
MASTER_SSID = "Master-Agro"
MASTER_PASS = "12345678"
MASTER_IP = "192.168.4.1"
PORT = 5000

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(MASTER_SSID, MASTER_PASS)

meu_mac = ubinascii.hexlify(sta.config('mac')).decode()
meu_id = None

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)

# ==========================================
# LOOP PRINCIPAL
# ==========================================
ultima_leitura = time.ticks_ms()
ultimo_envio = time.ticks_ms()

temp, hum, eco2, tvoc, aqi, lux = 0.0, 0.0, 0, 0, 0, 0.0

while True:
    agora = time.ticks_ms()
    
    # Leitura a cada 2 segundos (2000 ms)
    if time.ticks_diff(agora, ultima_leitura) >= 2000:
        
        if climate:
            try:
                temp, hum = climate.measure()
            except Exception as e:
                print("Erro leitura AHT21:", e)
        
        if air:
            try:
                air_data = air.get_data()
                eco2 = air_data.get("eCO2", 0)
                tvoc = air_data.get("TVOC", 0)
                aqi = air_data.get("AQI", 0)
            except Exception as e:
                print("Erro leitura ENS160:", e)
            
        if light:
            try:
                lux = light.luminance()
            except Exception as e:
                print("Erro leitura BH1750:", e)
            
        oled.fill(0)
        oled.text(f"T:{temp:.1f}C H:{hum:.1f}%", 0, 0)
        oled.text(f"CO2:{eco2} TVC:{tvoc}", 0, 14) 
        oled.text(f"AQI:{aqi} LUX:{lux:.0f}", 0, 28)
        
        if not sta.isconnected():
            oled.text("Rede: BUSCANDO", 0, 48)
        elif meu_id is None:
            oled.text("Rede: REGISTRANDO", 0, 48)
        else:
            oled.text(f"ID:{meu_id} Mestre:OK", 0, 48)
            
        oled.show()
        ultima_leitura = agora

    # Envio a cada 10 segundos (10000 ms)
    if time.ticks_diff(agora, ultimo_envio) >= 10000:
        if sta.isconnected():
            if meu_id is None:
                payload = json.dumps({"action": "register", "mac": meu_mac})
            else:
                payload = json.dumps({
                    "action": "data",
                    "id": meu_id,
                    "sensores": {
                        "temp": round(temp, 2), "hum": round(hum, 2),
                        "co2": eco2, "tvoc": tvoc, "aqi": aqi, "lux": round(lux, 2)
                    }
                })
                
            try:
                sock.sendto(payload.encode(), (MASTER_IP, PORT))
            except:
                pass
        ultimo_envio = agora

    # Recebimento não bloqueante
    try:
        data, _ = sock.recvfrom(1024)
        resposta = json.loads(data.decode())
        
        if resposta.get("status") == "registered":
            meu_id = resposta.get("id")
        elif resposta.get("status") == "error" and resposta.get("message") == "unregistered":
            meu_id = None
    except OSError:
        pass
    except Exception as e:
        print("Erro no pacote recebido:", e)

    time.sleep(0.1)
