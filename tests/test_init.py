# --------------------------------------------------------------------
# Copyright (c) 2024 Alexandre Bento Freire. All rights reserved.
# Licensed under the MIT license
# --------------------------------------------------------------------

import sys
import os
import unittest
import threading

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src', 'pytracetoix'))

from pytracetoix import d__, c__, init__  # noqa


class TestInitInputFormat(unittest.TestCase):

    def setUp(self):
        init__(format={'input': 'vk{name}:`cz{value}`', 'sep': ' | '})

    def call_equal(self, data, expected):
        self.assertEqual(data['output__'], expected)
        return False

    def test_display_format(self):
        d__([c__(i + 1) for i in range(2)],
            before=lambda data: self.call_equal(data, "vki0:`cz1` | vki1:`cz2` | "))

    def tearDown(self):
        init__()


class TestInitInputNoSepFormat(unittest.TestCase):

    def setUp(self):
        init__(format={'input': 'jk{name}:`lz{value}`'})

    def call_equal(self, data, expected):
        self.assertEqual(data['output__'], expected)
        return False

    def test_display_format(self):
        d__([c__(i + 1) for i in range(2)],
            before=lambda data: self.call_equal(data, "jki0:`lz1`jki1:`lz2`"))

    def tearDown(self):
        init__()


class TestInitResultFormat(unittest.TestCase):

    def setUp(self):
        init__(format={'result': 'pp{name}:`ii{value}`'})

    def call_equal(self, data, expected):
        self.assertEqual(data['output__'], expected)
        return False

    def test_display_format(self):
        d__([c__(i + 1) for i in range(2)],
            before=lambda data: self.call_equal(data, "pp_:`ii[1, 2]`"))

    def tearDown(self):
        init__()


class TestInitStream(unittest.TestCase):

    def setUp(self):
        self.stream = open("unit-test-file.txt", "w")
        init__(stream=self.stream)

    def test_display_format(self):
        d__([c__(i + 2) for i in range(2)])

    def tearDown(self):
        self.stream.close()
        with open("unit-test-file.txt", "r") as f:
            content = f.read()
        os.remove("unit-test-file.txt")
        self.assertEqual(content, "i0:`2` | i1:`3` | _:`[2, 3]`\n")
        init__()


class TestInitMultiThread(unittest.TestCase):

    def setUp(self):
        init__(multithreading=True)

    def call_equal(self, data, expected):
        self.assertEqual(data['output__'], expected)
        return False

    def test_display_format(self):
        d__([c__(i + 2) for i in range(2)],
            before=lambda data: self.call_equal(data, str(threading.get_ident()) + ": i0:`2` | i1:`3` | _:`[2, 3]`"))

    def tearDown(self):
        init__()


if __name__ == '__main__':
    unittest.main()
