from flask import Flask, app, render_template, request, jsonify

from pyecharts import options as opts
from pyecharts.charts import Bar, Page, Line, Tab, Grid, Liquid
from pyecharts.commons.utils import JsCode
from pyecharts.faker import Faker
from jinja2 import Markup

from distutils.util import strtobool

from time import sleep

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
    CONTROLLER_DICT.update(args)
    return args


@app.route('/controller-trans')
def trans_controller():
    # {light_switch: bool, fan_switch: bool}
    # for k, v in CONTROLLER_DICT.items():
    #     CONTROLLER_DICT[k] = 1 - (strtobool(v) if type(v) is str else v)

    print(CONTROLLER_DICT)
    return jsonify(CONTROLLER_DICT)


@app.route("/barChart")
def get_barChart():
    c = (
        Bar()
        .add_xaxis(Faker.choose())
        .add_yaxis("商家A", Faker.values())
        .add_yaxis("商家B", Faker.values())
        .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本演示", subtitle="我是副標題"))
        # .load_javascript()
    )
    # data_plot = Markup(c.render_embed())
    # data_plot = a.dump_options()

    return c.dump_options_with_quotes()
    # return a


@app.route("/humility")
def get_humility(value=29.6):
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
        .set_global_opts(title_opts=opts.TitleOpts(title="Liquid-数据精度"))
    )
    return c.dump_options_with_quotes()


def main():

    global CONTROLLER_DICT
    CONTROLLER_DICT = {}  # {light_switch: bool, fan_switch: bool}

    app.run(host='0.0.0.0', debug=True, port=8000)


if __name__ == "__main__":
    main()

    # page_simple_layout()
    # app.run()
