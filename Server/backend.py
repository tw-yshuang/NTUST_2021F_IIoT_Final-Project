import os, sys, shutil, time
import numpy as np
from datetime import datetime
from flask import Flask, app, render_template, request, jsonify
from paho.mqtt.client import Client
from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Line, Tab, Grid, Liquid
from pyecharts.commons.utils import JsCode
from pyecharts.faker import Faker
from jinja2 import Markup


from src.mqtt import get_mqtt_client
from src.db_tool import insert_db, select_db

app = Flask(__name__, static_folder="templates")


@app.route('/', methods=['GET', 'POST'])
def index():
    global CHART_DISPLAY, CHART_DAYS
    # if request.method == 'GET':
    #     lightON = True if 'true' == request.args.get('lightON', default=None, type=str) else False
    # print(request.args.get('lightON', default=None, type=bool))
    if request.method == 'POST':
        CHART_DISPLAY = request.form.get('sensor', type=str)
        CHART_DAYS = request.form.get('days', type=int)
        print(request.form.get('days', type=int))
        get_dayLine(CHART_DISPLAY, CHART_DAYS)
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


@app.route("/dayLine")
def get_dayLine(sensor=None, days=3):
    global CHART_DISPLAY, CHART_DAYS
    if sensor is None:
        sensor = CHART_DISPLAY
        days = CHART_DAYS
    snesor_dict = {'temperature': 0, 'humility': 1, 'illuminate': 2}
    days_data = [data_analysis(last_day=i) for i in range(days)]

    current_hr = int(datetime.fromtimestamp(time.time()).strftime("%H"))
    c = (
        Line()
        .set_global_opts(
            title_opts=opts.TitleOpts(title=sensor),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            datazoom_opts=[opts.DataZoomOpts()],
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
        .add_xaxis([(f'{current_hr + i}' if 24 - current_hr > i else f'{current_hr + i - 24}') for i in range(0, 24)])
    )
    for i in range(days):
        c.add_yaxis(
            f"{days - i} day",
            days_data[i][snesor_dict[sensor]],
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
            label_opts=opts.LabelOpts(is_show=True, position="top"),
            is_smooth=True,
        )

    return c.dump_options_with_quotes()


@app.route("/tab_charts")
def get_tab_charts():
    sensor_dict = {'temperature': 0, 'humility': 1, 'illuminate': 2}
    days_data = [data_analysis(last_day=i) for i in range(5)]
    current_hr = int(datetime.fromtimestamp(time.time()).strftime("%H"))
    tab = Tab()
    for k, v in sensor_dict.items():
        c = (
            Line()
            .set_global_opts(
                title_opts=opts.TitleOpts(title=k),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                datazoom_opts=[opts.DataZoomOpts()],
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            )
            .add_xaxis([(f'{current_hr + i}' if 24 - current_hr > i else f'{current_hr + i - 24}') for i in range(0, 24)])
        )
        for i in range(5):
            c.add_yaxis(
                f"{5 - i} day",
                days_data[i][v],
                areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
                label_opts=opts.LabelOpts(is_show=True, position="top"),
                is_smooth=True,
            )

        tab.add(c, k)
    tab.render('./templates/tab_charts.html')
    return render_template('tab_charts.html')


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


@app.route("/illuminate")
def get_illuminate():
    return jsonify(DEVICE_DICT[SENSOR_LIST[2]][:5])


@app.route("/temperature")
def get_temperature():
    return jsonify(DEVICE_DICT[SENSOR_LIST[0]])


def receive_edge(client, userdata, msg):
    # sensor_name = msg.topic.split('/')[-1]

    # op_signal = float(msg.payload.decode('utf-8')) if sensor_name != 'Motion' else bool(msg.payload.decode('utf-8'))

    data = msg.payload.decode('utf-8')[1:-1].split(', ')
    insert_db(data)
    DEVICE_DICT.update(dict(zip(SENSOR_LIST, data)))
    print(DEVICE_DICT)


def get_data(from_unix: time.time(), to_unix: time.time()):
    return select_db(
        (
            'Timestamp',
            f'{datetime.fromtimestamp(from_unix - 28800).strftime("%Y-%m-%d %H:%M:%S")}',
            f'{datetime.fromtimestamp(to_unix - 28800).strftime("%Y-%m-%d %H:%M:%S")}',
        )
    )


def data_analysis(last_day: int):
    # print(f'{datetime.fromtimestamp(time.time() - 3600).strftime("%Y-%m-%d %H:%M:%S")}')
    time_block = [[], [], []]
    last_day += 1
    for hr in range(0, 24):
        source = get_data(from_unix=time.time() - (24 - hr) * last_day * 60 * 60, to_unix=time.time() - (23 - hr) * last_day * 60 * 60)
        source = np.array(source, dtype=np.object_) if source != [] else np.array([[0, 0, 0, 0, 0]], dtype=np.object_)
        time_block[0].append(int(sum(source[:, 2]) / source.shape[0]))
        time_block[1].append(int(sum(source[:, 3]) / source.shape[0]))
        time_block[2].append(int(sum(source[:, 4]) / source.shape[0]))
        # t_mean = sum(source[:][2]) / len(source[:][2])
    return time_block


def main():
    db_path = './Data/sensor-data.db'

    if not os.path.exists(db_path):
        shutil.copy('./Data/default_sensor-data.db', db_path)
        print("Successfully copy file.")

    global DEVICE_DICT, SENSOR_LIST, CLIENT, CHART_DISPLAY, CHART_DAYS
    DEVICE_DICT = {'temperature': '25.0', 'humility': '44.3', 'illuminate': '506.2', 'motion': 'true'}
    SENSOR_LIST = ['temperature', 'humility', 'illuminate', 'motion']
    CLIENT = get_mqtt_client(msg_func=receive_edge)
    CHART_DISPLAY = 'humility'
    CHART_DAYS = 3

    app.run(host='0.0.0.0', debug=True, port=8000)


if __name__ == "__main__":

    main()

    # page_simple_layout()
    # app.run()
