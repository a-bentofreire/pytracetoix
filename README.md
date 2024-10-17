# Description

![PyPI - Version](https://img.shields.io/pypi/v/pytracetoix)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/a-bentofreire/pytracetoix/.github%2Fworkflows%2Fpython-package.yml)

[PyTraceToIX](https://www.devtoix.com/en/projects/pytracetoix) is an expression tracer designed for debugging Jinja2 templates, Flask web apps, lambdas, list comprehensions, method chaining, and expressions in general.

Code editors often cannot set breakpoints within these kinds of expressions, which requires significant code modifications to debug effectively.

For Jinja2 templates, the debug extension can be used, but it typically dumps the entire context, making it difficult to isolate specific issues. PyTraceToIX solves this by allowing developers to trace and write specific data directly to sys.stdout or a stream without altering the design or making any changes to the web application.

Additionally, PyTraceToIX can capture multiple inputs and their results, displaying them all in a single line, making it easier to view aggregated data and trace the flow of values.

PyTraceToIX offers a straightforward solution to these challenges, simplifying debugging while preserving the integrity of the original codebase.

It was designed to be simple, with easily identifiable functions that can be removed once the bug is found.

PyTraceToIX has 2 major functions:
- `c__` capture the input of an expression input. ex: `c__(x)`
- `d__` display the result of an expression and all the captured inputs. ex: `d__(c__(x) + c__(y))`

And 2 optional functions:
- `init__` initializes display format, output stream and multithreading.
- `t__` defines a name for the current thread.

If you find this project useful, please, read the [Support this Project](https://www.devtoix.com/en/projects/pytracetoix#support-this-project) on how to contribute.

## Features

- No external dependencies.
- Minimalist function names that are simple and short.
- Traces Results along with Inputs.
- Configurable Result and Input naming.
- Output to the `stdout` or a stream.
- Supports multiple levels.
- Capture Input method with customizable `allow` and `name` callbacks.
- Display Result method with customizable `allow`, `before`, and `after` callbacks.
- Result and Inputs can be reformatted and overridden.
- Configurable [formatting](https://www.devtoix.com/en/projects/pytracetoix#formatting) at global level and at function level.
- [Multithreading](https://www.devtoix.com/en/projects/pytracetoix#multithreading) support.

## JavaScript Version

This package is also available in JavaScript for similar debugging purposes. The JavaScript version, called **JsTraceToIX**, allows tracing input and output values during debugging and can be found on [JsTraceToIX](https://www.devtoix.com/en/projects/jstracetoix).

It offers the same `c__` and `d__` tracing functionality for JavaScript, supporting React, Vue, browser and Node.js environments.

## Installation

```bash
pip install pytracetoix
```

## Jinja2 templates Usage

In this example:
- A flask web app uses a Jinja2 template
- It generates a shopping card html table with product, quantity and final price

| Product | Qty | Final Price |
| ------- | --- | ----------- |
| Smartphone | 5 | 2500 |
| Wireless B | 50 | 49960 |
| Smartphone | 20 | 1990 |

- The product name is only the first 11 characters, but we need to know the full name.
- It only shows the final price which is Price * Qty - discount.
- The discount is dependent of the quantity.
- `c__` captures the complete name but doesn't change the design.
- `c__` captures the qty and labels it as Qty.
- `c__` captures the discount value.
- `d__` outputs to sys.stdout all the captured inputs and the final price.

The stdout will display these lines:

```plaintext
i0:`Smartphone 128GB` | qty:`5` | i2:`500` | discount:`0` | _:`2500`
i0:`Wireless Bluetooth Headphones` | qty:`50` | i2:`1000` | discount:`40` | _:`49960`
i0:`Smartphone 64GB Black` | qty:`20` | i2:`100` | discount:`10` | _:`1990`
```

Jinja2 template:

```html
<html lang="en">
<head><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet"></head>
<body>
    <div class="container mt-5">
        <h1>Shopping Cart</h1>
        <table class="table table-striped">
            <tr><th>Product</th><th>Qty</th><th>Final Price</th></tr>
            {% for item in purchases %}
            {% set product = products[item['product']] %}
            <tr>
                <td>{{ c__(product['name'])[0:10] }}</td>
                <td>{{ c__(item['qty'], name='qty') }}</td>
                <td>{{ d__(c__(product['price']) * item['qty']
                    - c__(discount(item['qty']), name='discount')) }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
```

app.py:

```python
from flask import Flask, render_template
from pytracetoix import c__, d__

app = Flask(__name__)

app.Jinja2_env.globals['d__'] = d__
app.Jinja2_env.globals['c__'] = c__

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
```

If the previous example, we add c__ to the discount function on app.py:

```python
def discount(qty): return c__(next((k, v) for k, v in DISCOUNTS.items() if k <= qty))[1]
```

It will add richer discount information to the output:

```plaintext
i0:`Smartphone 128GB` | qty:`5` | i2:`500` | i3:`(0, 0)` | discount:`0` | _:`2500`
i0:`Wireless Bluetooth Headphones` | qty:`50` | i2:`1000` | i3:`(50, 40)` | discount:`40` | _:`49960`
i0:`Smartphone 64GB Black` | qty:`20` | i2:`100` | i3:`(20, 10)` | discount:`10` | _:`1990`
```

## Detailed Usage and Examples

```python
from pytracetoix import d__, c__

[x, y, w, k, u] = [1, 2, 3, 4 + 4, lambda x:x]
#  expression
z = x + y * w + (k * u(5))

# Display expression with no inputs
z = d__(x + y * w + (k * u(5)))

# Output:
# _:`47`

# Display expression result with inputs
z = d__(c__(x) + y * c__(w) + (k * u(5)))

# Output:
# i0:`1` | i1:`3` | _:`47`

# Display expression result with inputs within an expression
z = d__(c__(x) + y * c__(w) + d__(k * c__(u(5), level=1)))

# Output:
# i0:`5` | _:`40`
# i0:`1` | i1:`3` | _:`47`

# lambda function
f = lambda x, y: x + (y + 1)
f(5, 6)

# Display lambda function result and inputs
f = lambda x, y: d__(c__(x) + c__(y + 1))
f(5, 6)

# Output:
# i0:`5` | i1:`7` | _:`12`

# Display lambda function inputs and result with input and result names
f = lambda x, y: d__(c__(x, name='x') + c__(y + 1, name='y+1'), name='f')
f(5, 6)

# Output:
# x:`5` | y+1:`7` | f:`12`

# list comprehension
l = [5 * y * x for x, y in [(10, 20), (30, 40)]]

# Display list comprehension with input and result names
l = d__([5 * c__(y, name=f"y{y}") * c__(x, name=lambda index, _, __: f'v{index}') for x, y in [(10, 20), (30, 40)]])
# Output:
# y20:`20` | v1:`10` | y40:`40` | v3:`30` | _:`[1000, 6000]`

# Display expression if `input count` is 2
d__(c__(x) + c__(y), allow=lambda data: data['input_count__'] == 2)
# Output:
# i0:`1` | i1:`2` | _:`3`

# Display expression if the first input value is 10.0
d__(c__(x) + c__(y), allow=lambda data: data['i0'] == 10.0)
# No output

# Display expression if the `allow_input_count` is 2, in this case if `x > 10`
d__(c__(x, allow=lambda index, name, value: value > 10) + c__(y),
        allow=lambda data: data['allow_input_count__'] == 2)
# No output

# Display list comprehension if the generated output has the text 10
d__([c__(x) for x in ['10', '20']], before=lambda data: '10' in data['output__'])
# Output:
# i0:`10` | i1:`20` | _:`['10', '20']`

# Display list comprehension and after call `call_after` if it was allowed to display
d__([c__(x) for x in ['10', '20']], allow=lambda data: data['allow_input_count__'] == 2,
        after=lambda data: call_after(data) if data['allow__'] else "")

# Display list comprehension with allow input override
d__([c__(x, allow=lambda index, name, value:value[0]) \
    for x in [('10', '20'), ('30', '40'), ('50', '60')]])
# i0:`10` | i1:`30` | i2:`50` | _:`[('10', '20'), ('30', '40'), ('50', '60')]`

# Display list comprehension with allow result override
d__([c__(x) for x in [('10', '20'), ('30', '40'), ('50', '60')]], \
     allow=lambda data:data['_'][0:2])
# i0:`('10', '20')` | i1:`('30', '40')` | i2:`('50', '60')` | _:`[('10', '20'), ('30', '40')]`

class Chain:
    def __init__(self, data):
        self.data = data

    def map(self, func):
        self.data = list(map(func, self.data))
        return self

    def filter(self, func):
        self.data = list(filter(func, self.data))
        return self


# A class with chain methods
Chain([10, 20, 30, 40, 50]).map(lambda x: x * 2).filter(lambda x: x > 70)

# Display the result and capture the map and filter inputs
d__(Chain([10, 20, 30, 40, 50]).map(lambda x: c__(x * 2)).filter(lambda x: c__(x > 70)).data)

# Output:
# i0:`20` | i1:`40` | i2:`60` | i3:`80` | i4:`100` | i5:`False` | i6:`False` | i7:`False` | i8:`True` | i9:`True` | _:`[80, 100]`

```

## Formatting

The `d__` function can override the default formatting, and it can also be defined at global level.

```python
from pytracetoix import init__

init__(format={
    'result': '{name}:`{value}`',
    'input': '{name}:`{value}`',
    'thread': '{id}: ',
    'sep': ' | ',
    'new_line': True
})
```

Formatting parameters:
- `result`: The result value format will be displayed.
- `input`: The input value format will be displayed.
- `sep`: The separator text between each input and the result.
- `new_line`: If `True` it will add a new line at the end of output.

## Multithreading

To activate the multithreading support:

```python
from pytracetoix import d__, c__, t__, init__

init__(multithreading=True)

## It displays the threadId: i0: `4` | _: `5`
def thread_function():
    d__(c__(4) + 1)

## It displays the something: i0: `4` | _: `5`
def thread_function_with_name():
    t__("something")
    d__(c__(4) + 1)

threads = []
for _ in range(5):
    thread = threading.Thread(target=thread_function)
    threads.append(thread)
threads.append(threading.Thread(target=thread_function_with_name))

for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```

## Metadata

The `d__` function callbacks `allow`, `before` and `after` will receive a parameter `data` with the allowed inputs plus the following `meta` items:

- `meta__`: list of meta keys including the name key.
- `thread_id__`: thread_id being executed
- `allow_input_count__`: total number of inputs that are allowed.
- `input_count__`: total number of inputs being captured.
- `allow__`: If false it was allowed. Use this for `after` callback.
- `output__`: Text passed to `before` without `new_line`.
- name: name parameter

## Documentation

 [Package Documentation](https://www.devtoix.com/docs/pytracetoix/en/)

## Support this Project

If you find this project useful, consider supporting it:

- Donate:

[![Donate via PayPal](https://www.paypalobjects.com/webstatic/en_US/i/btn/png/blue-rect-paypal-34px.png)](https://www.paypal.com/donate/?business=MCZDHYSK6TCKJ&no_recurring=0&item_name=Support+Open+Source&currency_code=EUR)

[![Buy me a Coffee](https://www.devtoix.com/assets/buymeacoffee-small.png)](https://buymeacoffee.com/abentofreire)

- Visit the project [homepage](https://www.devtoix.com/en/projects/pytracetoix)
- Give the project a ⭐ on [Github](https://github.com/a-bentofreire/pytracetoix)
- Spread the word
- Follow me:
  - [Github](https://github.com/a-bentofreire)
  - [LinkedIn](https://www.linkedin.com/in/abentofreire)
  - [Twitter/X](https://x.com/devtoix)

## License

MIT License

## Copyrights

(c) 2024 [Alexandre Bento Freire](https://www.a-bentofreire.com)
