import sys, os, shutil
import sqlite3

# sys.path.append(os.path.abspath(__package__))


def control_db(db_path: str = './Data/sensor-data.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    isRun = True

    while isRun:
        ctrl_code = int(input("1 insert | 2 update | 3 delete | 0 exit\n"))
        if ctrl_code == 0:
            isRun = False
        elif ctrl_code == 1:
            sql = ''' 
            INSERT INTO iiot_devices (Temperature, Humility, Illuminate, Motion) 
            VALUES ( 231.54, 564, 456.5, TRUE) 
            '''
        elif ctrl_code == 2:
            row_id = input("row_id = ")
            sql = f'''
            update iiot_devices
            set Temperature = 55.16
            WHERE ID={row_id};
            '''
        elif ctrl_code == 3:
            row_id = input("row_id = ")
            sql = f'''
            delete from iiot_devices
            WHERE ID={row_id};
            '''

        cursor.execute(sql)
        conn.commit()


def insert_db(data, db_path: str = './Data/sensor-data.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sql = f''' 
            INSERT INTO iiot_devices (Temperature, Humility, Illuminate, Motion) 
            VALUES ( {data[0]}, {data[1]}, {data[2]}, {data[3]}) 
            '''

    cursor.execute(sql)
    conn.commit()


def main():
    db_path = './Data/sensor-data.db'
    if not os.path.exists(db_path):
        shutil.copy('./Data/default_sensor-data.db', db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM `iiot_devices`;')
    records = cursor.fetchall()
    print(records)
    cursor.close()
    conn.close()


if __name__ == '__main__':
    from IoT_control import IoTController

    db_path = './sensor-data.db'

    if not os.path.exists(db_path):
        shutil.copy('./default_sensor-data.db', db_path)
        print("Successfully copy file.")

    iot = IoTController()
    while True:
        data = iot.recevice_data()
        insert_db(data, db_path)
