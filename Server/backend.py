import os, sys, shutil, time
from flask import Flask, app, render_template, request, jsonify
from paho.mqtt.client import Client
from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Line, Tab, Grid, Liquid
from pyecharts.commons.utils import JsCode
from pyecharts.faker import Faker
from jinja2 import Markup


from src.mqtt import get_mqtt_client
from src.db_tool import insert_db

app = Flask(__name__, static_folder="templates")


@app.route('/', methods=['GET', 'POST'])
def index():
    # if request.method == 'GET':
    #     lightON = True if 'true' == request.args.get('lightON', default=None, type=str) else False
    # print(request.args.get('lightON', default=None, type=bool))
    # if request.method == 'POST':
    #     print(request.args.get('isSwitch', default=None, type=bool))
    # sleep(5)
    # trans_controller()

    return render_template("index.html")


@app.route('/controller-receive', methods=['GET'])
def receive_controller():
    # aa = request.args
    # print(aa[0])
    args = request.args
    DEVICE_DICT.update(args)
    for device, isON in args.items():
        CLIENT.publish(topic=f'output/{device}', payload=isON, qos=2)
    return args


@app.route('/controller-trans')
def trans_controller():
    # {light_switch: bool, fan_switch: bool}
    # for k, v in DEVICE_DICT.items():
    #     DEVICE_DICT[k] = 1 - (strtobool(v) if type(v) is str else v)

    CLIENT.loop_start()
    print(DEVICE_DICT)
    return jsonify(DEVICE_DICT)


@app.route("/barChart")
def get_barChart():
    c = (
        Bar()
        .add_xaxis(["00:00~04:00", "04:00~8:00", "08:00~12:00", "12:00~16:00", "16:00~20:00", "20:00~00:00"])
        # .add_yaxis("01/09", Faker.values())
        .add_yaxis("01/09", Faker.values())
        .add_yaxis("01/10", Faker.values())
        .set_global_opts(title_opts=opts.TitleOpts(title="light-compare", subtitle="by Day"))
        # .load_javascript()
    )
    # data_plot = Markup(c.render_embed())
    # data_plot = a.dump_options()

    return c.dump_options_with_quotes()
    # return a


@app.route("/humility")
def get_humility(value=29.6):
    value = float(DEVICE_DICT[SENSOR_LIST[1]])
    value_ls = [value / 100, value * 1.05 / 100]
    c = (
        Liquid()
        .add(
            "lq",
            value_ls,
            label_opts=opts.LabelOpts(
                font_size=50,
                formatter=f'{value} %',
                position="inside",
            ),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title="Humility"))
    )
    return c.dump_options_with_quotes()


def receive_edge(client, userdata, msg):
    # sensor_name = msg.topic.split('/')[-1]

    # op_signal = float(msg.payload.decode('utf-8')) if sensor_name != 'Motion' else bool(msg.payload.decode('utf-8'))

    data = msg.payload.decode('utf-8')[1:-1].split(', ')
    print
    insert_db(data)
    DEVICE_DICT.update(dict(zip(SENSOR_LIST, data)))
    print(DEVICE_DICT)


def main():
    db_path = './Data/sensor-data.db'

    if not os.path.exists(db_path):
        shutil.copy('./Data/default_sensor-data.db', db_path)
        print("Successfully copy file.")

    global DEVICE_DICT, SENSOR_LIST, CLIENT
    DEVICE_DICT = {}  # {light_switch: bool, fan_switch: bool}
    SENSOR_LIST = ['Temperature', 'Humility', 'Illuminate', 'Motion']
    CLIENT = get_mqtt_client(msg_func=receive_edge)

    app.run(host='0.0.0.0', debug=True, port=8000)


if __name__ == "__main__":

    main()

    # page_simple_layout()
    # app.run()
