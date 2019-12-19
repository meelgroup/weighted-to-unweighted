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
    def __init__(self, origVars, origCls, vars, totalCount, eqWtVars):
        self.origVars = origVars
        self.origCls = origCls
        self.vars = vars
        self.totalCount = totalCount
        self.eqWtVars = eqWtVars


class Converter:

    def __init__(self, precision):
        self.precision = precision
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

    def encodeCNF(self, variable, kWeight, iWeight, origvars, origcls):
        cls = origcls
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

        if initWeight == 1:
            return 1, 0
        weight = math.ceil(initWeight*pow(2, self.precision))

        prec = self.precision
        while (weight % 2 == 0):
            weight = weight/2
            prec -= 1
        return weight, prec

    #  The code is straightforward chain formula implementation
    def transform(self, inputFile, outputFile):
        # read in input CNF
        with open(inputFile, 'r') as f:
            lines = f.readlines()

        writeLines = ''
        vars = 0
        cls = 0
        origVars = 0
        origCls = 0
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

            if line.strip()[0] == 'c':
                writeLines += str(line)
                continue

            if not foundHeader:
                print("ERROR: The 'p cnf VARS CLAUSES' header must be at the top of the CNF!")
                exit(-1)

            # parse independent set
            if line[:5] == "c ind":
                foundCInd = True
                for var in line.strip().split()[2:]:
                    if var == "0":
                        break
                    self.samplSet[int(var)] = 1
                continue

            # an actual clause
            if line.strip()[0].isdigit() or line.strip()[0] == '-':
                writeLines += str(line)

            # NOTE: we are skipping all the other types of things in the CNF
            #       for example, the weights
            continue

        if not foundHeader:
            print("ERROR: No header 'p cnf VARS CLAUSES' found in the CNF!")
            exit(-1)

        # if "c ind" was not found, then all variables are in the sampling set
        if not foundCInd:
            for i in range(1, vars+1):
                self.samplSet[i] = 1

        # weight parsing and CNF generation
        origWeight = {}
        indWeight = {}
        weightLine = ''
        equalWeightVars = 0
        for line in lines:
            if line.strip()[:2] == 'w ':
                fields = line.strip()[2:].split()
                var = int(fields[0])
                val = float(fields[1])

                # already has been declared, error
                if var in origWeight:
                    print("ERROR: Variable %d has TWO weights declared" % var)
                    print("ERROR: Please ONLY declare each variable's weight once")

                if var not in self.samplSet:
                    print("ERROR: Variable %d has a weight but is not part of the independent set" % var)
                    print("ERROR: Either remove the 'c ind' line or add this variable to it")
                    exit(-1)

                origWeight[var] = val
                self.samplSet[i] = 1
                kWeight, iWeight = self.parseWeight(val)
                if not((iWeight == 0 and kWeight == 1) or (val == 0.5)):
                    weightLine, vars, cls = self.encodeCNF(
                        var, kWeight, iWeight, vars, cls)
                else:
                    if iWeight == 0:
                        if kWeight == 1:
                            cls += 1
                            weightLine += str(var)+' 0\n'
                        if kWeight == 0:
                            cls += 1
                            weightLine += str(-var)+' 0\n'
                    if val == 0.5:
                        equalWeightVars += 1
                    indWeight[var] = 1
                writeLines += weightLine

        indWriteStr = 'c ind '
        count = 0
        if count % 10 != 0:
            indWriteStr += '0\n'

        origWtStr = ''
        for key in origWeight.keys():
            origWtStr += 'c o '+str(key)+' '+str(origWeight[key])+'\n'

        with open(outputFile, 'w') as f:
            f.write('p cnf '+str(vars)+' '+str(cls)+' \n')
            f.write(writeLines)

        return RetVal(origVars, origCls,
                      vars, cls, equalWeightVars)


####################################
# main function
####################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--prec", help="Precision (value of m)", type=int)
    parser.add_argument("inputFile", help="input File (in Weighted CNF format)")
    parser.add_argument("outputFile", help="output File (in Weighted CNF format)")
    args = parser.parse_args()

    if args.prec is None:
        print("ERROR: you must give the --prec option, e.g. --prec 7")
        exit(-1)

    startTime = time.time()
    c = Converter(precision=args.prec)
    ret = c.transform(args.inputFile, args.outputFile)
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
