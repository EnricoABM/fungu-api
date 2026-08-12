from machine import Pin, I2C, SPI
import ssd1306
import time
import json
import ubinascii
import network
import socket

# ==========================================
# HARDWARE E DISPLAY (Heltec V2)
# ==========================================
pino_vext = Pin(21, Pin.OUT)
pino_vext.value(0) 
time.sleep(0.1)

oled_reset = Pin(16, Pin.OUT)
oled_reset.value(0)
time.sleep(0.1)
oled_reset.value(1)

i2c_display = I2C(1, scl=Pin(15), sda=Pin(4), freq=100000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c_display)
oled.fill(0)
oled.text("Iniciando Mestre...", 0, 0)
oled.show()

CONFIG_FILE = "config.json"

def carregar_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def salvar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

config = carregar_config()
ssid = config.get("ssid")
password = config.get("password")
api_url = config.get("api_url", "http://192.168.1.50:8000/api/dados")

ap = network.WLAN(network.AP_IF)
sta = network.WLAN(network.STA_IF)

def modo_portal():
    ap.active(True)
    ap.config(essid="ESP-Mestre-Config", password="")
    ip = ap.ifconfig()[0]
    print(f"Modo AP ativo. Conecte em 'ESP-Mestre-Config' e acesse http://{ip}")
    
    oled.fill(0)
    oled.text("Modo AP Ativo", 0, 0)
    oled.text(f"IP: {ip}", 0, 14)
    oled.text("Configure via Web", 0, 28)
    oled.show()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    
    while True:
        conn, addr = s.accept()
        request = conn.recv(1024).decode('utf-8')
        
        if "POST" in request:
            try:
                body = request.split("\r\n\r\n")[1]
                params = {}
                for param in body.split("&"):
                    k, v = param.split("=")
                    params[k] = v.replace("+", " ").replace("%2F", "/").replace("%3A", ":").replace("%2E", ".")
                
                novo_config = {
                    "ssid": params.get("ssid"),
                    "password": params.get("password"),
                    "api_url": params.get("api_url")
                }
                salvar_config(novo_config)
                
                conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n<h1>Configurado com sucesso! Reiniciando...</h1>')
                time.sleep(2)
                machine.reset()
            except Exception as e:
                conn.send('HTTP/1.1 400 Bad Request\n\nErro ao salvar configuracao.')
        else:
            html = """<!DOCTYPE html>
<html>
<head><title>Config Mestre LoRa</title></head>
<body>
<h2>Configuracao do Mestre LoRa</h2>
<form method="POST">
SSID Wi-Fi: <input type="text" name="ssid"><br><br>
Senha Wi-Fi: <input type="password" name="password"><br><br>
API URL: <input type="text" name="api_url" value="http://192.168.1.50:8000/api/dados"><br><br>
<input type="submit" value="Salvar e Conectar">
</form>
</body>
</html>"""
            conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + html)
        conn.close()

if not ssid or not password:
    modo_portal()
else:
    sta.active(True)
    sta.connect(ssid, password)
    t = 0
    while not sta.isconnected() and t < 20:
        time.sleep(0.5)
        t += 1
    if not sta.isconnected():
        print("Falha ao conectar. Abrindo modo AP...")
        modo_portal()

# ==========================================
# CONFIGURAÇÃO LORA (RX)
# ==========================================
from sx127x import SX127x

spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(5), mosi=Pin(27), miso=Pin(19))
lora_pins = {
    'cs': Pin(18, Pin.OUT),
    'reset': Pin(14, Pin.OUT),
    'dio_0': Pin(26, Pin.IN)
}
lora_params = {
    'frequency': 915E6, 
    'tx_power_level': 14, 
    'signal_bandwidth': 125E3, 
    'spreading_factor': 8, 
    'coding_rate': 5
}

lora = SX127x(spi, pins=lora_pins, parameters=lora_params)
lora.receive()

# ==========================================
# GERENCIAMENTO DINÂMICO DE IDS
# ==========================================
tabela_nodes = {}
proximo_id = 1

def atribuir_id(mac_slave):
    global proximo_id
    if mac_slave not in tabela_nodes:
        tabela_nodes[mac_slave] = proximo_id
        proximo_id += 1
    return tabela_nodes[mac_slave]

# ==========================================
# ENVIO HTTP PARA API
# ==========================================
def enviar_para_api(url, payload):
    try:
        parts = url.split('/')
        host = parts[2]
        path = "/".join(parts[3:])
        port = 80
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        
        addr = socket.getaddrinfo(host, port)[0][-1]
        s = socket.socket()
        s.connect(addr)
        
        data = json.dumps(payload)
        http_req = f"POST /{path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/json\r\nContent-Length: {len(data)}\r\nConnection: close\r\n\r\n{data}"
        s.send(http_req.encode('utf-8'))
        s.close()
        return True
    except Exception as e:
        print("Erro HTTP API:", e)
        return False

# ==========================================
# LOOP PRINCIPAL
# ==========================================
ultimo_display = time.ticks_ms()
total_enviados = 0

while True:
    agora = time.ticks_ms()
    
    if lora.check_msg():
        payload_bytes = lora.read_payload()
        try:
            mensagem_str = payload_bytes.decode('utf-8').strip()
            pacote = json.loads(mensagem_str)
            
            mac = pacote.get("mac")
            dados = pacote.get("data")
            
            if mac and dados:
                node_id = atribuir_id(mac)
                
                payload_api = {
                    "id": node_id,
                    "mac": mac,
                    "sensores": dados
                }
                
                if enviar_para_api(api_url, payload_api):
                    total_enviados += 1
                    print(f"[API] Enviado Slave MAC {mac} -> ID: {node_id}")
                else:
                    print(f"[API] Falha ao enviar Slave MAC {mac}")
                
        except Exception as e:
            print("Erro no pacote LoRa:", e)
            
        lora.receive()

    if time.ticks_diff(agora, ultimo_display) >= 2000:
        oled.fill(0)
        oled.text("=== MESTRE LORA ===", 0, 0)
        oled.text(f"Nodes Ativos: {len(tabela_nodes)}", 0, 14)
        oled.text(f"Enviados API: {total_enviados}", 0, 28)
        
        wifi_status = "OK" if sta.isconnected() else "OFF"
        oled.text(f"WiFi/API: {wifi_status}", 0, 48)
        oled.show()
        ultimo_display = agora

    time.sleep(0.05)
