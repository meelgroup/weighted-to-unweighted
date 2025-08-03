#!/usr/bin/env python3
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

import time
import argparse
import random
import re


def transform(lines, outfile, perc, ignore_w):
    cnf = []
    ind = {}
    ind_found = False
    header_found = False
    maxvar = 0
    numcls = 0
    cls_actually = 0
    numvars = 0
    for line in lines:
        line = line.strip()
        line = re.sub(r'\s+', ' ', line)

        if line == "":
            print("ERROR: Empty line in CNF, that's not DIMACS!")
            exit(-1)

        if line.startswith("c ind ") or line.startswith("c p show "):
            ind_found = True
            at = None
            if line.startswith("c p show "):
                at = 3
            else: at = 2
            for v in line.split()[at:]:
                if v == "0":
                    break
                ind[int(v)] = 1
            continue

        if line.startswith("c p weight"):
            if not ignore_w:
                print("ERROR: the input CNF already contains weights!")
                exit(-1)
            continue

        if line.startswith("p cnf"):
            header_found = True
            numvars = int(line.split()[2])
            numcls = int(line.split()[3])
            continue

        if line.startswith("c"):
            cnf.append(line)
            continue

        # must be a clause from here on
        cls_actually += 1
        cnf.append(line)
        for lit in line.split():
            maxvar = max(abs(int(lit)), maxvar)

    if not header_found:
        print("ERROR: 'p cnf' header not found!")
        exit(-1)

    if cls_actually != numcls:
        print("ERROR: Header said there will be %d clauses, but there were %d" % (numcls, cls_actually))
        exit(-1)

    if not ind_found:
        for v in range(1, maxvar+1):
            ind[v] = 1

    if maxvar > numvars:
        print("ERROR: You are using a variable, %d, that's larger than what the 'p cnf' header declared")
        exit(-1)

    numvars = max(maxvar, numvars)

    # finally, write the CNF
    with open(outfile, "w") as f:
        f.write("p cnf %d %d\n" % (numvars, numcls))
        f.write("c ind ")
        for v,_ in ind.items():
            f.write("%d " % v)
        f.write("0\n")

        for c in cnf:
            f.write(c + "\n")

        for v,_ in ind.items():
            w = None

            # only add weight to specified percetage
            if random.uniform(0, 1) > perc:
                w = 0.5
            else:
                w = random.uniform(0, 1)

            f.write("c p weight %d %3.7f 0\n" % (v, w))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--perc", help="Percentage of variables to attach non-0.5 weight to. Default: 1.0",
        type=float, default=1.0)
    parser.add_argument(
        "--ignore", help="Ignore original weights", action="store_const", const=True)
    parser.add_argument(
        "--seed", help="Random number generator seed", type=int, default=1)
    parser.add_argument("inputFile", help="input File (in Weighted CNF format)")
    parser.add_argument("outputFile", help="output File (in Weighted CNF format)")
    args = parser.parse_args()

    random.seed(args.seed)

    startTime = time.time()

    # read in input CNF
    with open(args.inputFile, 'r') as f:
        lines = f.readlines()

    ret = transform(lines, args.outputFile, args.perc, args.ignore)
