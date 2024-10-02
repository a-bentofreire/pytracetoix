# --------------------------------------------------------------------
# Copyright (c) 2024 Alexandre Bento Freire. All rights reserved.
# Licensed under the MIT license
# --------------------------------------------------------------------

import sys
import os
import unittest
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src', 'pytracetoix'))

from pytracetoix import d__, c__, t__, init__  # noqa


class TestMultithreading(unittest.TestCase):
    def setUp(self):
        init__(multithreading=True)
        self._lock = threading.Lock()
        self.threads = []
        self.call_count = 0
        for _ in range(5):
            thread = threading.Thread(target=self.thread_function)
            self.threads.append(thread)

    def call_equal(self, data, call_count):
        self.assertEqual(data['output__'],
                         f'{threading.get_ident() if call_count != 2 else 'middle'}: i0:`{call_count}`'
                         + f' | i1:`{call_count + 1}` | _:`{call_count * 2 + 1}`')
        return False

    def thread_function(self):
        call_count = 0
        with self._lock:
            call_count = self.call_count
            if self.call_count == 2:
                t__("middle")
            self.call_count += 1

        d__(c__(call_count) + c__(call_count + 1), before=lambda _: False,
            after=lambda data: self.call_equal(data, call_count))
        time.sleep(0.001)

    def test_multithreading(self):
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()

    def tearDown(self):
        init__()


if __name__ == '__main__':
    unittest.main()
