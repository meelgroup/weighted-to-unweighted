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


# If you use this code for experiments, please cite the following paper:
# "From Weighted to UnWeighted Model Counting"
# by Supratik Chakraborty, Dror Fried, Kuldeep S. Meel, Moshe Y. Vardi
# Proc. of IJCAI 2016

import sys
import os
import math
import time
import argparse


class RetVal:
    def __init__(self, origVars, origCls, vars, totalCount):
        self.origVars = origVars
        self.origCls = origCls
        self.vars = vars
        self.totalCount = totalCount


class Converter:

    def __init__(self, precision,verbose=False):
        self.precision = precision
        self.verbose = verbose
        self.samplSet = {}

    def pushVar(self, variable, cnfClauses):
        cnfLen = len(cnfClauses)
        for i in range(cnfLen):
            cnfClauses[i].append(variable)
        return cnfClauses

    def getCNF(self, variable, binStr, sign, origVars):
        cnfClauses = []
        binLen = len(binStr)
        cnfClauses.append([binLen+1+origVars])
        for i in range(binLen):
            newVar = binLen-i+origVars
            if sign is False:
                newVar = -1*(binLen-i+origVars)
            if binStr[binLen-i-1] == '0':
                cnfClauses.append([newVar])
            else:
                cnfClauses = self.pushVar(newVar, cnfClauses)
        self.pushVar(variable, cnfClauses)
        return cnfClauses

    def encodeCNF(self, variable, kWeight, iWeight, origvars, cls):
        self.samplSet[origvars+1] = 1
        binStr = str(bin(int(kWeight)))[2:-1]
        binLen = len(binStr)
        for i in range(iWeight-binLen-1):
            binStr = '0'+binStr
        for i in range(iWeight-1):
            self.samplSet[origvars+i+2] = 1
        complementStr = ''
        for i in range(len(binStr)):
            if binStr[i] == '0':
                complementStr += '1'
            else:
                complementStr += '0'
        origCNFClauses = self.getCNF(-variable, binStr, True, origvars)

        writeLines = ''
        for i in range(len(origCNFClauses)):
            cls += 1
            for j in range(len(origCNFClauses[i])):
                writeLines += str(origCNFClauses[i][j])+' '
            writeLines += '0\n'

        currentVar = -variable
        cnfClauses = self.getCNF(variable, complementStr, False, origvars)
        for i in range(len(cnfClauses)):
            if cnfClauses[i] in origCNFClauses:
                continue
            cls += 1
            for j in range(len(cnfClauses[i])):
                writeLines += str(cnfClauses[i][j])+' '
            writeLines += '0\n'

        vars = origvars+iWeight
        return writeLines, vars, cls

    # return the number of bits needed to represent the weight (2nd value returned)
    # along with the weight:bits ratio
    def parseWeight(self, initWeight):
        assert self.precision > 1, "Precision must be at least 2"
        assert initWeight >= 0.0, "Weight must not be below 0.0"
        assert initWeight <= 1.0, "Weight must not be above 1.0"

        if self.verbose:
            print("Query for weight %3.5f" % (initWeight))

        weight = round(initWeight*pow(2, self.precision))
        prec = self.precision
        if self.verbose:
            print("weight %3.5f prec %3d" % (weight, prec))

        while weight % 2 == 0 and prec > 0:
            weight = weight/2
            prec -= 1

            if self.verbose:
                print("weight %3.5f prec %3d" % (weight, prec))

        if self.verbose:
            print("for %f returning: weight %3.5f prec %3d" % (initWeight, weight, prec))

        return weight, prec

    #  The code is straightforward chain formula implementation
    def transform(self, lines, outputFile):
        origCNFLines = ''
        vars = 0
        cls = 0
        origVars = 0
        origCls = 0
        maxvar = 0
        foundCInd = False
        foundHeader = False
        for line in lines:
            if len(line) == 0:
                print("ERROR: The CNF contains an empty line.")
                print("ERROR: Empty lines are NOT part of the DIMACS specification")
                print("ERROR: Remove the empty line so we can parse the CNF")
                exit(-1)

            if line.strip()[:2] == 'p ':
                fields = line.strip().split()
                vars = int(fields[2])
                cls = int(fields[3])
                origVars = vars
                origCls = cls
                foundHeader = True
                continue

            # parse independent set
            if line[:5] == "c ind":
                foundCInd = True
                for var in line.strip().split()[2:]:
                    if var == "0":
                        break
                    self.samplSet[int(var)] = 1
                continue

            if line.strip()[0] == 'c':
                origCNFLines += str(line)
                continue

            if not foundHeader:
                print("ERROR: The 'p cnf VARS CLAUSES' header must be at the top of the CNF!")
                exit(-1)

            # an actual clause
            if line.strip()[0].isdigit() or line.strip()[0] == '-':
                for lit in line.split():
                    maxvar = max(abs(int(lit)), maxvar)
                origCNFLines += str(line)

            # NOTE: we are skipping all the other types of things in the CNF
            #       for example, the weights
            continue

        if maxvar > vars:
            print("ERROR: CNF contains var %d but header says we only have %d vars" % (maxvar, vars))
            exit(-1)

        print("Header says vars: %d  maximum var used: %d" % (vars, maxvar))

        if not foundHeader:
            print("ERROR: No header 'p cnf VARS CLAUSES' found in the CNF!")
            exit(-1)

        # if "c ind" was not found, then all variables are in the sampling set
        if not foundCInd:
            for i in range(1, vars+1):
                self.samplSet[i] = 1

        # weight parsing and CNF generation
        origWeight = {}
        transformCNFLines = ''
        for line in lines:
            if line.strip()[:2] == 'w ':
                fields = line.strip()[2:].split()
                var = int(fields[0])
                val = float(fields[1])

                # already has been declared, error
                if var in origWeight:
                    print("ERROR: Variable %d has TWO weights declared" % var)
                    print("ERROR: Please ONLY declare each variable's weight ONCE")
                    exit(-1)

                if var not in self.samplSet:
                    print("ERROR: Variable %d has a weight but is not part of the sampling set" % var)
                    print("ERROR: Either remove the 'c ind' line or add this variable to it")
                    exit(-1)

                origWeight[var] = val
                self.samplSet[var] = 1
                kWeight, iWeight = self.parseWeight(val)

                if self.verbose:
                    representedW = float(kWeight)/(2**iWeight)
                    # print("kweight: %5d iweight: %5d" % (kWeight, iWeight))
                    print("var: %5d orig-weight: %3.6f kweight: %5d iweight: %5d represented-weight: %3.6f"
                          % (var, val, kWeight, iWeight, representedW))

                if (val == 0.5) or (kWeight == 1 and iWeight == 1):
                    # Trivial case.
                    # It's either 0.5 exactly or we cannot distinguish
                    pass
                elif iWeight == 0:
                    # for the case where it's effectively 1.0 or 0.0
                    cls += 1
                    if kWeight == 1:
                        transformCNFLines += str(var)+' 0\n'
                    if kWeight == 0:
                        transformCNFLines += str(-var)+' 0\n'
                else:
                    # we have to encode to CNF the translation
                    eLines, vars, cls = self.encodeCNF(var, kWeight, iWeight, vars, cls)
                    transformCNFLines += eLines

        with open(outputFile, 'w') as f:
            f.write('p cnf '+str(vars)+' '+str(cls)+' \n')
            f.write('c ind ')
            for k in self.samplSet:
                f.write("%d " % k)
            f.write("0\n")

            f.write(origCNFLines)
            f.write(transformCNFLines)

        return RetVal(origVars, origCls, vars, cls)


####################################
# main function
####################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose", help="Verbose debug printing", action="store_const",
        const=True)
    parser.add_argument("--prec", help="Precision (value of m)", type=int, default=7)
    parser.add_argument("inputFile", help="input File (in Weighted CNF format)")
    parser.add_argument("outputFile", help="output File (in Weighted CNF format)")
    args = parser.parse_args()

    if args.prec is None:
        print("ERROR: you must give the --prec option, e.g. --prec 7")
        exit(-1)

    startTime = time.time()
    c = Converter(precision=args.prec, verbose=args.verbose)

    # read in input CNF
    with open(args.inputFile, 'r') as f:
        lines = f.readlines()

    ret = c.transform(lines, args.outputFile)

    # ret looks like:
    #    wtVars
    #    origVars
    #    origCls
    #    vars
    #    totalCount
    #    eqWtVars

    print("Orig vars: %-7d New Vars: %-7d" % (ret.origVars, ret.vars))
    print("Time to transform: %0.3f s" % (time.time()-startTime))
    exit(0)
