import paho.mqtt.client as mqtt

from app.api.dependencies import get_session
class MqttClient:
    def __init__(self, broker_ip: str, port: int, topic: str, handler, keepalive=60):
        self.__broker_ip = broker_ip
        self.__port = port
        self.__topic = topic
        self.__keepalive = keepalive
        self._handler = handler

        self.__client = mqtt.Client()

        self.__client.on_connect = self._on_connect
        self.__client.on_subscribe = self._on_subscribe
        self.__client.on_message = self._on_message

    def start_connection(self):
        self.__client.connect(host=self.__broker_ip, port=self.__port, keepalive=self.__keepalive)
        self.__client.loop_start()

    def stop_connection(self):
        self.__client.loop_stop()
        self.__client.disconnect()

    def _on_connect(self, client, userdate, flags, rc):
        if rc == 0:
            print("MQTT Client Connected")
            self.__client.subscribe(self.__topic)
        else:
            print(f"Error connecting to the MQTT Client")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"Client Subscribed at {self.__topic} QoS: {granted_qos}")

    def _on_message(self, client, userdate, message):
        self._handler.handle(message)