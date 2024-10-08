# --------------------------------------------------------------------
# Copyright (c) 2024 Alexandre Bento Freire. All rights reserved.
# Licensed under the MIT license
# --------------------------------------------------------------------

import threading
import sys
from typing import Union, Callable, Dict, Any

Format = Dict[str, Union[str, bool]]
Allow_Result = Union[bool, Any]

"""
Format Type -- Defines how result and input values will be formatted.

Parameters:
    result: The format of the result value to be displayed. Defaults to '{name}:`{value}`'.
    input: The format of the input value to be displayed. Defaults to '{name}:`{value}`'.
    thread: The format of the thread id format to be displayed. Defaults to '{id}: '.
    sep: The separator text between each input and the result. Defaults to ' | '.
    new_line: If True it will add a new line at the end of output.
"""
DEFAULT_FORMAT: Format = {
    'result': '{name}:`{value}`',
    'input': '{name}:`{value}`',
    'thread': '{id}: ',
    'sep': ' | ',
    'new_line': True
}
_stream = sys.stdout
_multithreading = False
_format = DEFAULT_FORMAT
_inputs_per_threads = {}
_thread_names = {}
_lock = threading.Lock()


def init__(stream: Any = None, multithreading: bool = False, format: Format = DEFAULT_FORMAT):
    """
    Initializes global settings of the tracing tool.

    Args:
        stream (stream, optional):
          The output stream to write the output lines.
          Defaults to sys.stdout.
        multithreading (bool, optional):
          If True, it prefixes the output with `thread_id:`.
          Defaults to False.
        format (Format, optional):
          Format dictionary.
          Defaults to DEFAULT_FORMAT.
    """
    global _stream, _multithreading, _format, _inputs_per_threads, _thread_names
    with _lock:
        _stream = stream or sys.stdout
        _multithreading = multithreading
        _format = format
        _inputs_per_threads = {}
        _thread_names = {}


def t__(name: str = None, thread_id: int = None):
    """
    Assigns a name to a thread.

    If no **name** is provided, it generates a name based on the number of threads.

    If no thread_id is provided, uses the current thread ID.

    Args:
        name (str, optional):
          The name for the thread.
          Defaults to 't%d' where %d is the number of threads.
        thread_id (int, optional):
          The ID of the thread.
          Defaults to the current thread ID.
    """
    global _thread_names
    with _lock:
        _thread_names[thread_id or threading.get_ident()] = name or f't{len(_thread_names)}'


def c__(value: Any,
        name: Union[str, Callable[[int, int, Any], str]] = None,
        allow: Union[bool, Callable[[int, str, Any], str], Allow_Result] = True,
        level: int = 0):
    """
    Captures the input value for the current thread.

    If no name is provided, it generates a default name.

    Args:
        value (Any): The input value to store.
        name (Union[str, Callable[[int, int, Any], str]], optional):
          The name of the input.
          Defaults to 'i%d' where %d is the number of inputs for the thread.
        allow (Callable[[int, str, Any], str]], optional):
          A function or value to allow tracing the input. **allow** is called before **name**.
          If it returns True or False, it will allow or disallow respectively.
          If it returns not bool, then it will display the allow result instead of the input value.
        level (int, optional):
          The level number to be used when there is more than one **d__** within the same
          expression or function.
          Defaults to 0.

    Returns:
        value

    Examples:
        >>> c__(x)

        >>> c__(x, name="var-name")
        >>> c__(x, name=lambda index, allow_index, value: f"{index}")

        >>> [c__(i, allow=lambda index, name, value: index > 2) for i in range(5)]
        >>> [c__(x, allow=lambda index, name, value: value == 20) for x in [10, 20, 30]]

        >>> z = d__(c__(outside_1) + y * c__(outside_2) + d__(k * c__(inside(5), level=1)))

    """
    global _inputs_per_threads
    with _lock:
        thread_id = threading.get_ident()
        if thread_id not in _inputs_per_threads:
            _inputs_per_threads[thread_id] = [{'index__': 0, 'meta__': ['meta__', 'index__']}]
        while len(_inputs_per_threads[thread_id]) <= level:
            _inputs_per_threads[thread_id].append({'index__': 0, 'meta__': ['meta__', 'index__']})
        inputs = _inputs_per_threads[thread_id][level]
        index = inputs['index__']
        meta_count = len(inputs['meta__'])
        if callable(name):
            name = name(index, len(inputs) - meta_count, value)
        name = name or f'i{len(inputs) - meta_count}'
        display_value = value
        if callable(allow):
            allow = allow(index, name, value)
            if type(allow) is not bool:
                display_value = allow
                allow = True
        if allow is None or allow:
            _inputs_per_threads[thread_id][level][name] = display_value
        _inputs_per_threads[thread_id][level]['index__'] = index + 1

    return value


def d__(value: Any,
        name: str = '_',
        allow: Callable[[Dict[str, Any]], Allow_Result] = None,
        before: Callable[[Dict[str, Any]], bool] = None,
        after: Callable[[Dict[str, Any]], None] = None,
        inputs: Dict[str, Any] = None,
        format: Format = None):
    """
    Displays formatted result and inputs for the current thread using a given format.

    Optionally calls **allow**, **before** and **after** functions with the data.

    **allow**, **before** and **after** will receive a parameter **data** with the allowed inputs.
     With the following **meta** values:

    - **meta__**: List of meta keys including the name key.
    - **thread_id__**: Id of the thread being executed.
    - **allow_input_count__**: Total number of inputs that are allowed.
    - **input_count__**: Total number of inputs being captured.
    - **allow__**: If **false** it was allowed. Use this for **after** callback.
    - **output__**: Text passed to **before** without **new_line**.
    - **name**: **value** parameter.

    Args:
        value (Any): The result to trace.
        name (str, optional):
          The name of the function being traced.
          Defaults to '_'.
        allow (Callable[[Dict[str, Any]], bool], optional):
          A function to call to allow tracing.
          If it returns False, tracing is skipped but after is still called.
          If it returns not bool, then it will display the allow result instead of the result.
        before (Callable[[Dict[str, Any]], bool], optional):
          A function to call before displaying the output.
          If it returns False, tracing is skipped.
        after (Callable[[Dict[str, Any]], None], optional):
          A function to call after displaying the output.
          After is always called even if not allow.
        inputs (Dict[str, Any], optional):
          Dictionary of additional inputs.
        format (Format, optional):
          Alternative output format.

    Returns:
        value

    Examples:
        >>> d__(x)
        >>> d__(c__(x) + c__(y))

        >>> d__(c__(x) + c__(y, name="y"), name="output")

        >>> d__(c__(x) + c__(y), allow=lambda data: data['input_count__'] == 2)
        >>> d__(c__(x) + c__(y), allow=lambda data: data['i0'] == 10.0)
        >>> d__(c__(x, allow=lambda index, name, value: value > 10) + c__(y),
                allow=lambda data: data['allow_input_count__'] == 2)

        >>> d__([c__(x) for x in ['10', '20']], before=lambda data: '10' in data['output__'])

        >>> d__([c__(x) for x in ['1', '2']], allow=lambda data: data['allow_input_count__'] == 2,
                after=lambda data: call_after(data) if data['allow__'] else "")

"""
    global _inputs_per_threads, _thread_names, _stream, _multithreading, _format

    def replace_macro(format, key, value):
        return format.replace('{name}', key).replace('{value}', str(value))

    with _lock:
        thread_id = threading.get_ident()
        levels = _inputs_per_threads.get(thread_id, [{}])
        data = levels[len(levels) - 1] | (inputs or {})
        data['thread_id__'] = thread_id
        data['input_count__'] = data.get('index__') or 0
        data['allow__'] = True
        data['meta__'] = (data.get('meta__') or ['meta__']) + [
            'allow__', 'allow_input_count__', 'input_count__', 'thread_id__', name]
        data[name] = value
        if data.get('index__'):
            del data['index__']
            data['meta__'].remove('index__')
        data['allow_input_count__'] = len(data) - len(data['meta__']) + 1

        if allow is not None:
            allow = allow(data)
            if type(allow) is not bool:
                data[name] = allow
                allow = True

        if allow is None or allow:
            format = format or _format
            output = format['thread'] \
                .replace('{id}', _thread_names.get(thread_id, str(thread_id))) \
                if _multithreading and format.get('thread') else ''
            if format.get('input'):
                for key, val in data.items():
                    if key not in data['meta__']:
                        output += replace_macro(format['input'], key, val) + \
                            (format.get('sep') or '')

            if format.get('result'):
                output += replace_macro(format['result'], name, data[name])
            data['meta__'] += ['output__']
            data['output__'] = output
            if before is None or before(data):
                _stream.write(data['output__'] + ('\n' if format.get('new_line') or True else ''))
                _stream.flush()
        else:
            data['allow__'] = False

        if after is not None:
            after(data)

        if _inputs_per_threads.get(thread_id):
            _inputs_per_threads[thread_id].pop()
            if len(_inputs_per_threads[thread_id]) == 0:
                _inputs_per_threads.pop(thread_id, None)

    return value
