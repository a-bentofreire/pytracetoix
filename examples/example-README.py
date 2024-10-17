#!/usr/bin/env python3
import sys
import os
import threading

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

def call_after(s):
    return True


from pytracetoix import d__, c__, init__, t__

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
# Output:
# No output

# Display list comprehension if the generated output has the text 10
d__([c__(x) for x in ['10', '20']], before=lambda data: '10' in data['output__'])
# Output:
# i0:`10` | i1:`20` | _:`['10', '20']`

def u(s):
    print(s)
    return s

# Display list comprehension and after call `call_after` if it was allowed to display
d__([c__(x) for x in ['10', '20']], allow=lambda data: u(data)['allow_input_count__'] == 2,
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
