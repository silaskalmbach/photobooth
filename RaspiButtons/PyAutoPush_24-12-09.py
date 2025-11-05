import pyautogui
import random
import paho.mqtt.client as mqtt

broker = "localhost"  # Geändert von "mqtt-broker" zu "localhost"
port = 1883
topic = "button/push"
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = "PhotoFrame"
password = "%dma@2q@!Jesah$xS"

def press_button():
    pyautogui.press('tab')
    pyautogui.press('space')

def connect_mqtt():
    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"Failed to connect: {reason_code}")
        else:
            print("Connected to MQTT Broker!")

    def on_disconnect(client, userdata, reason_code, properties):
        print(f"Disconnected from MQTT Broker: {reason_code}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt.Client):
    def on_message(client, userdata, message):
        print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
        press_button()

    def on_subscribe(client, userdata, mid, reason_code_list, properties):
        if reason_code_list[0].is_failure:
            print(f"Broker rejected subscription: {reason_code_list[0]}")
        else:
            print(f"Subscription successful with QoS: {reason_code_list[0].value}")

    client.on_subscribe = on_subscribe
    client.subscribe(topic)
    client.on_message = on_message

def main():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    main()