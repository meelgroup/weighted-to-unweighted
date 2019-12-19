#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Kuldeep S Meel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import unittest
from weightcount import Converter

class TestMyMethods(unittest.TestCase):
    def test_parseWeight(self):
        c = Converter(precision=10)

        # 1 of 4 is 0.25
        self.assertEqual(c.parseWeight(0.25), (1.0, 2))

        # 1 of 8 is 0.125
        self.assertEqual(c.parseWeight(0.125), (1.0, 3))

        # 3 of 4 is 0.75
        self.assertEqual(c.parseWeight(0.75), (3.0, 2))

        # 3 of 4 is 0.75 -- just about enough bits here
        c = Converter(precision=2)
        self.assertEqual(c.parseWeight(0.75), (3.0, 2))

        # precision must be at least 2 bits
        with self.assertRaises(AssertionError):
            c = Converter(precision=1)
            c.parseWeight(0.75)


if __name__ == '__main__':
    unittest.main()
