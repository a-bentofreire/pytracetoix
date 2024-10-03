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

from pytracetoix import d__, c__, init__  # noqa


class TestInitInputFormat:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        init__(format={'input': 'vk{name}:`cz{value}`', 'sep': ' | '})

        yield
        init__()

    def call_equal(self, data, expected):
        assert data['output__'] == expected
        return False

    def test_display_format(self):
        d__([c__(i + 1) for i in range(2)],
            before=lambda data: self.call_equal(data, "vki0:`cz1` | vki1:`cz2` | "))


class TestInitInputNoSepFormat:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        init__(format={'input': 'jk{name}:`lz{value}`'})
        yield
        init__()

    def call_equal(self, data, expected):
        assert data['output__'] == expected
        return False

    def test_display_format(self):
        d__([c__(i + 1) for i in range(2)],
            before=lambda data: self.call_equal(data, "jki0:`lz1`jki1:`lz2`"))


class TestInitResultFormat:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        init__(format={'result': 'pp{name}:`ii{value}`'})
        yield
        init__()

    def call_equal(self, data, expected):
        assert data['output__'] == expected
        return False

    def test_display_format(self):
        d__([c__(i + 1) for i in range(2)],
            before=lambda data: self.call_equal(data, "pp_:`ii[1, 2]`"))


class TestInitStream:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, tmpdir):
        tmp_filename = tmpdir.join("unit-test-file.txt")
        self.stream = open(tmp_filename, "w")
        init__(stream=self.stream)
        yield
        self.stream.close()
        with open(tmp_filename, "r") as f:
            content = f.read()
        os.remove(tmp_filename)
        assert content == "i0:`2` | i1:`3` | _:`[2, 3]`\n"
        init__()

    def test_display_format(self):
        d__([c__(i + 2) for i in range(2)])


class TestInitMultiThread:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        init__(multithreading=True)
        yield
        init__()

    def call_equal(self, data, expected):
        assert data['output__'] == expected
        return False

    def test_display_format(self):
        d__([c__(i + 2) for i in range(2)],
            before=lambda data: self.call_equal(data, str(threading.get_ident()) + ": i0:`2` | i1:`3` | _:`[2, 3]`"))


if __name__ == '__main__':
    pytest.main()
