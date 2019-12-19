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


def pushVar(variable, cnfClauses):
    cnfLen = len(cnfClauses)
    for i in range(cnfLen):
        cnfClauses[i].append(variable)
    return cnfClauses


def getCNF(variable, binStr, sign, origTotalVars):
    cnfClauses = []
    binLen = len(binStr)
    cnfClauses.append([binLen+1+origTotalVars])
    for i in range(binLen):
        newVar = binLen-i+origTotalVars
        if sign is False:
            newVar = -1*(binLen-i+origTotalVars)
        if binStr[binLen-i-1] == '0':
            cnfClauses.append([newVar])
        else:
            cnfClauses = pushVar(newVar, cnfClauses)
    pushVar(variable, cnfClauses)
    return cnfClauses


def encodeCNF(variable, kWeight, iWeight, origtotalVars, origtotalClaus, independentSet, precision, runIndex):
    totalClaus = origtotalClaus
    independentSet[origtotalVars+1] = 1
    binStr = str(bin(int(kWeight)))[2:-1]
    binLen = len(binStr)
    for i in range(iWeight-binLen-1):
        binStr = '0'+binStr
    for i in range(iWeight-1):
        independentSet[origtotalVars+i+2] = 1
    complementStr = ''
    for i in range(len(binStr)):
        if binStr[i] == '0':
            complementStr += '1'
        else:
            complementStr += '0'
    origCNFClauses = getCNF(-variable, binStr, True, origtotalVars)

    writeLines = ''
    for i in range(len(origCNFClauses)):
        totalClaus += 1
        for j in range(len(origCNFClauses[i])):
            writeLines += str(origCNFClauses[i][j])+' '
        writeLines += '0\n'

    currentVar = -variable
    cnfClauses = getCNF(variable, complementStr, False, origtotalVars)
    for i in range(len(cnfClauses)):
        if cnfClauses[i] in origCNFClauses:
            continue
        totalClaus += 1
        for j in range(len(cnfClauses[i])):
            writeLines += str(cnfClauses[i][j])+' '
        writeLines += '0\n'

    totalVars = origtotalVars+iWeight
    return writeLines, totalVars, totalClaus, independentSet


def parseWeights(initWeight, precision):
    if initWeight == 1:
        return 1, 0
    weight = math.ceil(initWeight*pow(2, precision))
    while (weight % 2 == 0):
        weight = weight/2
        precision -= 1
    return weight, precision


#  The code is straightforward chain formula implementation
def transform(inputFile, outputFile, precision, runIndex):
    # read in input CNF
    with open(inputFile, 'r') as f:
        lines = f.readlines()

    writeLines = ''
    independentSet = {}
    totalVars = 0
    origTotalVars = 0
    origTotalClaus = 0
    totalClaus = 0
    for line in lines:
        if (line.strip()[:2] == 'p '):
            fields = line.strip().split()
            totalVars = int(fields[2])
            totalClaus = int(fields[3])
            origTotalVars = totalVars
            origTotalClaus = totalClaus
            continue
        if line.strip()[0].isdigit() or line.strip()[0] == 'c' or line.strip()[0] == '-':
            writeLines += str(line)

    # TODO: parse sampling set up above and use that instead
    for i in range(1, totalVars+1):
        independentSet[i] = 1

    # weight parsing and CNF generation
    origWeight = {}
    indWeight = {}
    weightLine = ''
    equalWeightVars = 0
    for line in lines:
        if line.strip()[:2] == 'w ':
            fields = line.strip()[2:].split()
            variable = int(fields[0])
            val = float(fields[1])

            origWeight[variable] = val
            kWeight, iWeight = parseWeights(val, precision)
            if not((iWeight == 0 and kWeight == 1) or (val == 0.5)):
                weightLine, totalVars, totalClaus, independentSet = encodeCNF(
                    variable, kWeight, iWeight, totalVars, totalClaus,
                    independentSet, precision, runIndex)
            else:
                if iWeight == 0:
                    if kWeight == 1:
                        totalClaus += 1
                        weightLine += str(variable)+' 0\n'
                    if kWeight == 0:
                        totalClaus += 1
                        weightLine += str(-variable)+' 0\n'
                if val == 0.5:
                    equalWeightVars += 1
                indWeight[variable] = 1
            writeLines += weightLine

    indWriteStr = 'c ind '
    count = 0
    wtVarCount = 0
    if (count % 10 != 0):
        indWriteStr += '0\n'
    origWtStr = ''
    for key in origWeight.keys():
        origWtStr += 'c o '+str(key)+' '+str(origWeight[key])+'\n'

    with open(outputFile, 'w') as f:
        f.write('p cnf '+str(totalVars)+' '+str(totalClaus)+' \n')
        f.write(writeLines)

    return wtVarCount, origTotalVars, origTotalClaus, totalVars, totalClaus, equalWeightVars


####################################
# main function
####################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--prec", help="Precision (value of m)", type=int)
    parser.add_argument("--runindex", help="run index", type=int, default=1)
    parser.add_argument("inputFile", help="input File (in Weighted CNF format)")
    parser.add_argument("outputFile", help="output File (in Weighted CNF format)")
    args = parser.parse_args()

    if args.prec is None:
        print("ERROR: you must give the --prec option, e.g. --prec 7")
        exit(-1)

    startTime = time.time()
    wtVars, origTotalVars, origTotalClaus, totalVars, totalCount, eqWtVars = transform(
        args.inputFile, args.outputFile, args.prec, args.runindex)
    print("Orig vars: %-7d New Vars: %-7d" % (origTotalVars, totalVars))
    print("Time to transform: %0.3f s" % (time.time()-startTime))
    exit(0)

    ####################################
    # this is some log -- NOT needed.
    initialFileSuffix = args.inputFile.split('/')[-1][:-4]
    logFile = 'Logs/'+str(initialFileSuffix)+'_'+str(args.runindex)+'.txt'
    with open(logFile, 'w') as f:
        f.write('transform:::'+str(time.time()-startTime)+':0\n')
        f.write('Stats:'+str(wtVars)+':'+str(origTotalVars)+':'+str(
            origTotalClaus)+':'+str(totalVars)+':'+str(totalCount)+':'+str(args.prec)+':0')
