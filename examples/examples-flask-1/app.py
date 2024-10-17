#!/usr/bin/env python3
from flask import Flask, render_template
from pytracetoix import c__, d__

app = Flask(__name__)

app.jinja_env.globals['d__'] = d__
app.jinja_env.globals['c__'] = c__

DISCOUNTS = {50: 40, 20: 10, 10: 5, 0: 0}
PRODUCTS = {
    'WB50CC': {'name': 'Wireless Bluetooth Headphones', 'price': 1000},
    'PH20XX': {'name': 'Smartphone 128GB', 'price': 500},
    'PH50YY': {'name': 'Smartphone 64GB Black', 'price': 100}
}

PURCHASES = [
    {'product': 'PH20XX', 'qty': 5},
    {'product': 'WB50CC', 'qty': 50},
    {'product': 'PH50YY', 'qty': 20}
]


def discount(qty): return next((k, v) for k, v in DISCOUNTS.items() if k <= qty)[1]


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', products=PRODUCTS, purchases=PURCHASES, discount=discount)


if __name__ == '__main__':
    app.run(debug=True)
