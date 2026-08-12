# Dependências

* Python 3.11
* Postgres
* Mosquitto
* Docker (Opcional)

# Como executar

* Faça um clone do projeto
```bash
git clone https://github.com/EnricoABM/fungu-api.git
cd fungu-api
```

* Crie um ambiente virtual
```bash
python -m venv venv
source ./venv/bin/activate
```

* Instale as dependencias
```bash
pip install requirements.txt
```

* Inicie a execução do postgres:
```bash
# Para instalação nativa
sudo systemctl start postgresql

# Docker (Opcional)
sudo docker run --name fungo_db -p 5432:5432 -e POSTGRES_PASSWORD=password -di postgres
```

* Crie o banco de dados dentro do postgres:
```bash
psql -U postgres    

# ou

sudo docker exec -ti fungo_db psql -U postgres
```

```sql
CREATE DATABASE fungo_db;
```

* Copie e configure as variáveis do ambiente por meio do arquivo `.env.example`
```bash
cp .env.example .env
```

* Execute as migrações para o banco de dados:
```bash
alembic upgrade head

# Caso tenha problemas com PATH do sistema
./venv/bin/python ./venv/bin/alembic upgrade head
```

* Inicie o broker MQTT
```bash
mosquito -v
```

* Inicie o servidor em outro terminal
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

## Consumindo a API

* Endpoints: Os endpoints podem ser acessados por meio da URL `http://127.0.0.1/docs`
* MQTT: A API está configurada para escutar o tópico configurado em `MQTT_TOPIC`, caso tenha instalado o serviço do mosquitto, use o comando para realizar uma requisição ao broker e salvar no banco de dados:
```bash
mosquitto_pub \                                                            
    -h localhost \
    -p 1883 \
    -t "fungo/ola" \
    -m '{"temperatura": 25.4, "umidade": 63.2, "luminosidade": 450.0, "aqi": 35, "tvoc": 120}'
```
