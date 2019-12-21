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
        c = Converter(precision=7)
        c.verbose = True
        # returns kWeight/iWeight combo

        # trivial cases
        self.assertEqual(c.parseWeight(1.0), (1, 0))
        self.assertEqual(c.parseWeight(0.0), (0, 0))

        # 1 of 4 is 0.25
        self.assertEqual(c.parseWeight(0.25), (1, 2))

        # 1 of 8 is 0.125
        self.assertEqual(c.parseWeight(0.125), (1, 3))

        # 3 of 4 is 0.75
        self.assertEqual(c.parseWeight(0.75), (3, 2))

        # close to 0.5 should give me 1,1
        self.assertEqual(c.parseWeight(0.5), (1, 1))
        self.assertEqual(c.parseWeight(0.49888), (1, 1))
        self.assertEqual(c.parseWeight(0.4987), (1, 1))
        self.assertEqual(c.parseWeight(0.5003), (1, 1))

        # for small precision, we are in a mess
        c.precision = 3
        self.assertEqual(c.parseWeight(0.0001), (0, 0))
        self.assertEqual(c.parseWeight(0.9999), (1, 0))

        # for larger precision, we are good
        c.precision = 13
        self.assertNotEquals(c.parseWeight(0.0001), (0, 0))
        self.assertNotEquals(c.parseWeight(0.9999), (1, 0))

        # for small precision, we should get 1,0 / 0,0 here
        c.precision = 4
        self.assertEqual(c.parseWeight(0.9977877), (1, 0))
        self.assertEqual(c.parseWeight(0.0022123), (0, 0))

        # 3 of 4 is 0.75 -- just about enough bits here
        c = Converter(precision=2)
        self.assertEqual(c.parseWeight(0.75), (3, 2))

        # precision must be at least 2 bits
        with self.assertRaises(AssertionError):
            c = Converter(precision=1)
            c.parseWeight(0.75)

    def test_encodeCNF(self):
        c = Converter(precision=10)

        # 2 out of 2**3 (i.e. 0.125)
        iWeight, kWeight = 1, 1
        var = 1
        origvars = 20
        cls = 20
        eLines, vars, cls = c.encodeCNF(var, iWeight, kWeight, origvars, 0)
        print("%s" % eLines)
        print("new vars: ", vars-origvars)
        print("cls: ", cls)


if __name__ == '__main__':
    unittest.main()
