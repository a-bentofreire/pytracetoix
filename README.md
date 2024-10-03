# Description

![PyPI - Version](https://img.shields.io/pypi/v/pytracetoix)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/a-bentofreire/pytracetoix/.github%2Fworkflows%2Fpython-package.yml)

[PyTraceToIX](https://www.devtoix.com/en/projects/pytracetoix) is an expression tracer for debugging lambdas, list comprehensions, method chaining, and expressions.

Code editors can't set breakpoints inside expressions, lambda functions, list comprehensions, and chained methods, forcing significant code changes to debug such code.

PyTraceToIX provides a straightforward solution to this problem.

It was designed to be simple, with easily identifiable functions that can be removed once the bug is found.

PyTraceToIX has 2 major functions:
- `c__` capture the input of an expression input. ex: `c__(x)`
- `d__` display the result of an expression and all the captured inputs. ex: `d__(c__(x) + c__(y))`

And 2 optional functions:
- `init__` initializes display format, output stream and multithreading.
- `t__` defines a name for the current thread.

If you find this project useful, please, read the [Support this Project](https://www.devtoix.com/en/projects/pytracetoix#support-this-project) on how to contribute.

## Features

- [Multithreading](https://www.devtoix.com/en/projects/pytracetoix#multithreading) support.
- Simple and short minimalist function names.
- Result with Inputs tracing.
- Configurable [formatting](https://www.devtoix.com/en/projects/pytracetoix#formatting) at global level and at function level.
- Configurable result and input naming.
- Output to the stdout or a stream.
- Multiple levels.
- Capture Input method with `allow` and `name` callback.
- Display Result method with `allow`, `before` and `after` callbacks.

## Installation

```bash
pip install pytracetoix
```

## Usage

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

#  list comprehension
l = [5 * y * x for x, y in [(10, 20), (30, 40)]]

# Display list comprehension with input and result names
l = d__([5 * c__(y, name=f"y{y}") * c__(x, name=lambda index, _, __: f'v{index}') for x, y in [(10, 20), (30, 40)]])

# Output:
# y20:`20` | v1:`10` | y40:`40` | v3:`30` | _:`[1000, 6000]`

# Display expression if `input count` is 2
d__(c__(x) + c__(y), allow=lambda data: data['input_count__'] == 2)

# Display expression if the first input value is 10.0
d__(c__(x) + c__(y), allow=lambda data: data['i0'] == 10.0)

# Display expression if the `allow_input_count` is 2, in this case if `x > 10`
d__(c__(x, allow=lambda index, name, value: value > 10) + c__(y),
        allow=lambda data: data['allow_input_count__'] == 2)

# Display expression if the generated output has the text 10
d__([c__(x) for x in ['10', '20']], before=lambda data: '10' in data['output__'])

# Display expression and after call `call_after` if it was allowed to display
d__([c__(x) for x in ['10', '20']], allow=lambda data: data['allow_input_count__'] == 2,
        after=lambda data: call_after(data) if data['allow__'] else "")

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
    'sep': ' | ',
    'new_line': True
})
```

Formatting parameters:
- `result`: The result value format will be displayed.
- `input`: The result value format will be displayed.
- `sep`: The separator text between each input and the result.
- `new_line`: If True it will add a new line at the end of output.

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
    t("something")
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

 The `allow`, `before` and `after` will receive a parameter `data` with the allowed inputs plus the following `meta` items:

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
