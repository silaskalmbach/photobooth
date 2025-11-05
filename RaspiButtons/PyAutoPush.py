import pyautogui

import random
from paho.mqtt import client as mqtt_client


broker = "mqtt-broker"
port = 1883
topic = "button/push"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = "PhotoFrame"
password = "%dma@2q@!Jesah$xS"


def press_button():
    # pyautogui.press('enter') 
    # Press tab
    pyautogui.press('tab')
    # Press space
    pyautogui.press('space')

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        press_button()

    client.subscribe(topic)
    client.on_message = on_message

def main():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    main()
