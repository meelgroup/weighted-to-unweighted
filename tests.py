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
import random
import math
from weightcount import Converter

verbose = False


def get_transl_err(prec, w):
    c = Converter(precision=prec)

    # 2 out of 2**3 (i.e. 0.125)
    iWeight, kWeight = c.parseWeight(w)
    print("iweight: %3d kweight: %3d prec: %3d w: %3.15f" % (iWeight, kWeight, prec, w))
    var = 1
    origvars = 20
    cls = 20
    eLines, vars, cls = c.encodeCNF(var, iWeight, kWeight, origvars, 0)
    newvars = vars-origvars
    if verbose:
        print("%s" % eLines)
        print("new vars: ", newvars)
        print("cls: ", cls)

    ok = {}
    ba = {}
    ok[True] = 0
    ok[False] = 0
    ba[True] = 0
    ba[False] = 0
    ok_tot = 0
    ba_tot = 0
    for x in range(2**(newvars+1)):
        setting = {}
        for i in range(1, newvars+1):
            setting[origvars+(newvars+1-i)] = bool((x >> i) & 1)
        setting[var] = bool((x >> 0) & 1)
        #print(setting)

        overall_val = True
        for line in eLines.split("\n"):
            val = False
            if line == "":
                continue

            #print("line.split:", line.split())
            for lit in line.split(" "):
                lit = int(lit)
                if lit == 0:
                    continue

                if lit > 0:
                    if setting[lit]:
                        val = True

                if lit < 0:
                    if not setting[-lit]:
                        val = True

            #print("val:", val)
            if not val:
                overall_val = False
                break

        #print("overall val:", overall_val)
        if overall_val:
            ok[setting[var]] += 1
            ok_tot += 1
        else:
            ba[setting[var]] += 1
            ba_tot += 1

    print("->OK[true]: %d/%d OK[false] = %d/%d" % (ok[True], ok_tot, ok[False], ok_tot))
    print("->Diff: %3.10f vs %3.10f" % (w, ok[True]/ok_tot))

    error = abs(w-ok[True]/ok_tot)
    print("->Diff: %3.10f" % (error))
    return error


class TestMyMethods(unittest.TestCase):
    def test_parseWeight(self):
        c = Converter(precision=7)
        c.verbose = False
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
        self.assertNotEqual(c.parseWeight(0.0001), (0, 0))
        self.assertNotEqual(c.parseWeight(0.9999), (1, 0))

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
        self.assertEqual(get_transl_err(10, 0.0), 0)
        self.assertEqual(get_transl_err(10, 1.0), 0)


if __name__ == '__main__':
    random.seed(1)
    #get_transl_err(10, 1.0)
    #get_transl_err(10, 0.0)
    #get_transl_err(10, 0.5)

    total_err = 0
    max_err = 0
    min_err = 1.0
    errs = []
    for x in range(1000):
        err = get_transl_err(10, random.uniform(0.0, 1.0))
        total_err += err
        errs.append(err)
        max_err = max(err, max_err)
        min_err = min(min_err, err)

    errs = sorted(errs)
    print("avg error:", total_err/1000.0)
    print("min error:", min_err)
    print("max error:", max_err)
    print("median error:", errs[math.ceil(len(errs)/2)])
    assert max_err < 1/(2**10)

    unittest.main()
