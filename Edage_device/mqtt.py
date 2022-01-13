import paho.mqtt.client as mqtt
from time import sleep
import json

# 當地端程式連線伺服器得到回應時，要做的動作
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # 將訂閱主題寫在on_connet中
    # 如果我們失去連線或重新連線時
    # 地端程式將會重新訂閱
    client.subscribe("output/+")


# 當接收到從伺服器發送的訊息時要進行的動作
def on_message(client, userdata, msg):
    # 轉換編碼utf-8才看得懂中文
    print(msg.topic + " " + msg.payload.decode('utf-8'))

    # TODO control device(fan, light)


def on_publish(client, userdata, mid):
    print("message published")


def get_mqtt_client(username: str, userpassword:str, ip:str, msg_func: on_message = on_message):

    # 連線設定
    # 初始化地端程式
    client = mqtt.Client()

    # 設定連線的動作
    client.on_connect = on_connect

    # 設定接收訊息的動作
    client.on_message = msg_func

    # 設定登入帳號密碼
    client.username_pw_set(username, userpassword)

    # 設定連線資訊(IP, Port, 連線時間)
    client.connect(ip, 1883, 60)

    # 開始連線，執行設定的動作和處理重新連線問題
    # 也可以手動使用其他loop函式來進行連接
    # client.loop_forever()
    client.loop_start()

    return client


if __name__ == '__main__':
    client = get_mqtt_client()
    i = 0
    while True:

        print("in loop")
        payload = {'i': i}
        client.publish(topic="input/t", payload=json.dumps(payload), qos=1)
        client.publish(topic="input/tbbb", payload=json.dumps("bbbb"), qos=1)
        i += 1
        sleep(3)
