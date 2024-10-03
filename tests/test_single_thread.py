# --------------------------------------------------------------------
# Copyright (c) 2024 Alexandre Bento Freire. All rights reserved.
# Licensed under the MIT license
# --------------------------------------------------------------------

import sys
import os
import pytest
import threading

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), 'src', 'pytracetoix'))

from pytracetoix import d__, c__  # noqa


class TestSingleThread:

    def call_equal(self, data, expected):
        assert data['output__'] == expected
        return False

    def test_lambda_no_inputs(self):
        (lambda o: d__(o + 1, before=lambda data: self.call_equal(data, "_:`16`")))(15)

    def test_lambda_string(self):
        (lambda o: d__(c__(o) + c__(o + 1), before=lambda data: self.call_equal(data, "i0:`5` | i1:`6` | _:`11`")))(5)

    def test_lambda_array(self):
        (lambda o: d__(c__(o) + c__([o[0] + 1]),
         before=lambda data: self.call_equal(data, "i0:`[7]` | i1:`[8]` | _:`[7, 8]`")))([7])

    def test_expression_levels(self):
        [x, y, w, k, u] = [1, 2, 3, 4 + 4, lambda x:x]
        d__(c__(x) + y * c__(w) + d__(k * c__(u(5), level=1),
                                      before=lambda data: self.call_equal(data, "i0:`5` | _:`40`")),
            before=lambda data: self.call_equal(data, "i0:`1` | i1:`3` | _:`47`"))

    def test_comprehension_array(self):
        d__(list(filter(lambda ext: c__(ext) == '.jpg', ['.png', '.jpg', '.gif'])),
            before=lambda data: self.call_equal(data, "i0:`.png` | i1:`.jpg` | i2:`.gif` | _:`['.jpg']`"))

    def test_lambda_input_name(self):
        (lambda o: d__(c__(o, name='p1'), before=lambda data: self.call_equal(data, "p1:`6` | _:`6`")))(6)

    def test_comprehension_double_input_name(self):
        d__([5 * c__(y, name=f"y{x}")*c__(x, name=f'x{y}') for x, y in [(10, 20), (30, 40)]],
            before=lambda data: self.call_equal(data, "y10:`20` | x20:`10` | y30:`40` | x40:`30` | _:`[1000, 6000]`"))

    def test_lambda_display_name(self):
        (lambda o: d__(c__(o) + 1, name='f2', before=lambda data: self.call_equal(data, "i0:`8` | f2:`9`")))(8)

    def test_capture_allow_index(self):
        d__([c__(i, allow=lambda index, _, __: index == 1 or index == 4) for i in range(6)],
            before=lambda data: self.call_equal(data, "i0:`1` | i1:`4` | _:`[0, 1, 2, 3, 4, 5]`"))

    def test_capture_allow_name(self):
        d__([c__(i, allow=lambda _, name, __: name[1] in '012') for i in range(6)],
            before=lambda data: self.call_equal(data, "i0:`0` | i1:`1` | i2:`2` | _:`[0, 1, 2, 3, 4, 5]`"))

    def test_capture_allow_value(self):
        d__([c__(i, allow=lambda _, __, value: value > 2 and value < 5) for i in range(10)],
            before=lambda data: self.call_equal(data, "i0:`3` | i1:`4` | _:`[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]`"))

    def test_capture_allow_index_with_name_index(self):
        d__([c__(i, allow=lambda index, _, __: index == 1 or index == 4, name=lambda index, _, __: f'x{index+1}') for i in range(6)],
            before=lambda data: self.call_equal(data, "x2:`1` | x5:`4` | _:`[0, 1, 2, 3, 4, 5]`"))

    def test_capture_allow_index_with_name_allow_index(self):
        d__([c__(i, allow=lambda index, _, __: index == 1 or index == 4, name=lambda _, allow_index, __: f'y{allow_index}') for i in range(6)],
            before=lambda data: self.call_equal(data, "y0:`1` | y1:`4` | _:`[0, 1, 2, 3, 4, 5]`"))

    def test_capture_allow_index_with_name_allow_value(self):
        d__([c__(i, allow=lambda index, _, __: index == 1 or index == 4, name=lambda _, __, value: f'z{value}') for i in range(6)],
            before=lambda data: self.call_equal(data, "z1:`1` | z4:`4` | _:`[0, 1, 2, 3, 4, 5]`"))

    def test_display_allow_allow_input_count__(self):
        d__([c__(i, allow=lambda index, _, __: index > 1 and index < 4) for i in range(5)],
            allow=lambda data: data['allow_input_count__'] == 2,
            before=lambda data: self.call_equal(data, "i0:`2` | i1:`3` | _:`[0, 1, 2, 3, 4]`"))

        d__([c__(i, allow=lambda index, _, __: index > 1 and index < 4) for i in range(5)],
            allow=lambda data: data['allow_input_count__'] != 2,
            after=lambda data: data.get("output__") is None)

    def test_display_allow_input_count__(self):
        d__([c__(i, allow=lambda index, _, __: index > 1 and index < 4) for i in range(5)],
            allow=lambda data: data['input_count__'] == 5,
            before=lambda data: self.call_equal(data, "i0:`2` | i1:`3` | _:`[0, 1, 2, 3, 4]`"))

        d__([c__(i, allow=lambda index, _, __: index > 1 and index < 4) for i in range(5)],
            allow=lambda data: data['input_count__'] != 5,
            after=lambda data: data.get("output__") is None)

    def test_display_allow_thread_id__(self):
        d__([c__(i) for i in range(1)],
            allow=lambda data: data['thread_id__'] == threading.get_ident(),
            before=lambda data: self.call_equal(data, "i0:`0` | _:`[0]`"))

        d__([c__(i) for i in range(1)],
            allow=lambda data: data['thread_id__'] != threading.get_ident(),
            after=lambda data: data.get("output__") is None)

    def test_display_after(self):
        d__([c__(i) for i in range(2)],
            before=lambda _: False,
            after=lambda data: self.call_equal(data, "i0:`0` | i1:`1` | _:`[0, 1]`"))

    def test_display_format(self):
        d__([c__(i + 1) for i in range(2)],
            format={'input': 'k{name}:`z{value}`', 'sep': ' | '},
            before=lambda data: self.call_equal(data, "ki0:`z1` | ki1:`z2` | "))

        d__([c__(i + 1) for i in range(2)],
            format={'input': 'k{name}:`z{value}`'},
            before=lambda data: self.call_equal(data, "ki0:`z1`ki1:`z2`"))

        d__([c__(i + 1) for i in range(2)],
            format={'result': 'ff{name}:`kk{value}`'},
            before=lambda data: self.call_equal(data, "ff_:`kk[1, 2]`"))

    def test_clear_inputs(self):
        d__([c__(i, name=lambda index, _, __: f'u{index}') for i in range(2)], before=lambda _: False)

        d__([c__(i) for i in range(2)],
            before=lambda data: self.call_equal(data, "i0:`0` | i1:`1` | _:`[0, 1]`"))

    def test_add_inputs(self):
        d__([c__(i) for i in range(2)],
            inputs={'u1': 2, 'k2': ['ab', 'cd']},
            before=lambda data: self.call_equal(data, "i0:`0` | i1:`1` | u1:`2` | k2:`['ab', 'cd']` | _:`[0, 1]`"))


if __name__ == '__main__':
    pytest.main()
