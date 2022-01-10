import sys, os, shutil, json

from IoT_control import IoTController
from db_tool import insert_db
from mqtt import get_mqtt_client
from distutils.util import strtobool


def on_message(client, userdata, msg, isDubug: bool = True):
    op_name = msg.topic.split('/')[-1]
    if isDubug:
        op_name = msg.topic.split('/')[-1]
        op_signal = int(msg.payload.decode('utf-8'))
        print(f"want to execute op_{op_name}(isON={op_signal})")

    getattr(IOT_CON, f'op_{op_name}')(isON=strtobool(msg.payload.decode('utf-8')))


def main():
    db_path = './sensor-data.db'

    if not os.path.exists(db_path):
        shutil.copy('./default_sensor-data.db', db_path)
        print("Successfully copy file.")

    client = get_mqtt_client(msg_func=on_message)

    sensor_list = ['Temperature', 'Humility', 'Illuminate', 'Motion']
    while True:
        data = IOT_CON.recevice_data()
        insert_db(data, db_path)
        # data_dict = dict(zip(sensor_list, data))
        for k, v in dict(zip(sensor_list, data)).items():
            client.publish(f'input/{k}', v, qos=1)


if __name__ == '__main__':
    global IOT_CON
    IOT_CON = IoTController()
    main()
