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
LOGDIR = 'Log'


def ProcessLine(line, originalVars, variable):
    fields = line.strip().split()[:-1]
    finalLine = ''
    for field in fields:
        sign = int(field)/abs(int(field))
        if (field == '1'):
            finalLine += str(sign*variable)+' '
        else:
            finalLine += str(sign*(originalVars+abs(int(field))-1))+' '
    finalLine += '0\n'
    return finalLine


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
        if (sign == False):
            newVar = -1*(binLen-i+origTotalVars)
        if (binStr[binLen-i-1] == '0'):
            cnfClauses.append([newVar])
        else:
            cnfClauses = pushVar(newVar, cnfClauses)
    pushVar(variable, cnfClauses)
    return cnfClauses


def EncodeCNF(variable, kWeight, iWeight, origtotalVars, origtotalClaus, independentSet, precision, runIndex):
    writeLines = ''
    totalVars = origtotalVars+iWeight
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
        if (binStr[i] == '0'):
            complementStr += '1'
        else:
            complementStr += '0'
    origCNFClauses = getCNF(-variable, binStr, True, origtotalVars)

    for i in range(len(origCNFClauses)):
        totalClaus += 1
        for j in range(len(origCNFClauses[i])):
            writeLines += str(origCNFClauses[i][j])+' '
        writeLines += '0\n'
    currentVar = -variable
    cnfClauses = getCNF(variable, complementStr, False, origtotalVars)
    for i in range(len(cnfClauses)):
        if (cnfClauses[i] in origCNFClauses):
            continue
        totalClaus += 1
        for j in range(len(cnfClauses[i])):
            writeLines += str(cnfClauses[i][j])+' '
        writeLines += '0\n'
    return writeLines, totalVars, totalClaus, independentSet


def ParseWeights(initWeight, precision):
    if (initWeight == 1):
        return 1, 0
    weight = math.ceil(initWeight*pow(2, precision))
    while (weight % 2 == 0):
        weight = weight/2
        precision -= 1
    return weight, precision
#  @tempCNFFile is temporary file.
#  The code is straightforward chain formula implementation
#


def Transform(inputFile, outputFile, tempCNFFile, precision, runIndex):
    f = open(inputFile, 'r')
    lines = f.readlines()
    f.close()
    writeLines = ''
    weightLine = ''
    independentSet = {}
    totalVars = 0
    origTotalVars = 0
    origTotalClaus = 0
    totalClaus = 0
    indWeight = {}
    origWeight = {}
    minWeight = 0
    for line in lines:
        if (line.strip()[:2] == 'p '):
            fields = line.strip().split()
            totalVars = int(fields[2])
            totalClaus = int(fields[3])
            origTotalVars = totalVars
            origTotalClaus = totalClaus
            continue
        if (line.strip()[0].isdigit() or line.strip()[0] == 'c' or line.strip()[0] == '-'):
            writeLines += str(line)
    for i in range(1, totalVars+1):
        independentSet[i] = 1
    f = open(tempCNFFile, 'w')
    f.write('p cnf '+str(totalVars)+' '+str(totalClaus)+'\n')
    f.write(writeLines)
    f.close()
    equalWeightVariables = 0
    for line in lines:
        if (line.strip()[:2] == 'w '):
            fields = line.strip()[2:].split()
            variable = int(fields[0])
            if (float(fields[1]) < 1):
                minWeight += math.log(min(float(fields[1]),
                                          1-float(fields[1])), 2)
            origWeight[variable] = float(fields[1])
            kWeight, iWeight = ParseWeights(float(fields[1]), precision)
            if (not((iWeight == 0 and kWeight == 1) or (float(fields[1]) == 0.5))):
                weightLine, totalVars, totalClaus, independentSet = EncodeCNF(
                    variable, kWeight, iWeight, totalVars, totalClaus, independentSet, precision, runIndex)
            else:
                if (iWeight == 0):
                    if (kWeight == 1):
                        totalClaus += 1
                        weightLine += str(variable)+' 0\n'
                    if (kWeight == 0):
                        totalClaus += 1
                        weightLine += str(-variable)+' 0\n'
                if (float(fields[1]) == 0.5):
                    equalWeightVariables += 1
                indWeight[variable] = 1
            writeLines += weightLine
    indWtWrteStr = ''
    indWriteStr = 'c ind '
    count = 0
    wtVarCount = 0
    if (count % 10 != 0):
        indWriteStr += '0\n'
    origWtStr = ''
    for key in origWeight.keys():
        origWtStr += 'c o '+str(key)+' '+str(origWeight[key])+'\n'
    f = open(outputFile, 'w')
    f.write('p cnf '+str(totalVars)+' '+str(totalClaus)+' \n')
    f.write(writeLines)
    f.close()
    return wtVarCount, origTotalVars, origTotalClaus, totalVars, totalClaus, minWeight, equalWeightVariables


def ensureDirectory(path):
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)
    return


####################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-precision", help="Precision (value of m)", type=int, default=7)
    parser.add_argument("-timeout", help="timeout", type=int, default=300)
    parser.add_argument("-runIndex", help="runIndex", type=int, default=1)
    parser.add_argument(
        "inputFile", help="input File (in Weighted CNF format)")
    args = parser.parse_args()
    precision = args.precision
    timeout = args.timeout
    runIndex = args.runIndex
    inputFile = args.inputFile
    tmpDir = os.getenv("TMPDIR", "temp")

    # initialization
    ensureDirectory(tmpDir+'/')
    ensureDirectory('Logs/')

    initialFileSuffix = inputFile.split('/')[-1][:-4]
    outputFile = tmpDir+'/'+str(initialFileSuffix)+'_'+str(runIndex)+'.txt'
    logFile = 'Logs/'+str(initialFileSuffix)+'_'+str(runIndex)+'.txt'
    outCNFFile = tmpDir+'/'+str(initialFileSuffix)+'_'+str(runIndex)+'.cnf'
    tempCNFFile = tmpDir+'/'+str(initialFileSuffix) + \
        '_temp_'+str(runIndex)+'.cnf'
    startTime = time.time()
    wtVars, origTotalVars, origTotalClaus, totalVars, totalCount, minWeight, eqWtVars = Transform(
        inputFile, outCNFFile, tempCNFFile, precision, runIndex)

    endTime = time.time()
    writeStr = 'Transform:::'+str(endTime-startTime)+':0\n'
    writeStr += 'Stats:'+str(wtVars)+':'+str(origTotalVars)+':'+str(
        origTotalClaus)+':'+str(totalVars)+':'+str(totalCount)+':'+str(precision)+':0\n'
    f = open(logFile, 'w')
    f.write(writeStr)
    f.close()
    cmd = './doalarm -t real ' + \
        str(timeout)+' ./sharpSAT -q -c 3000 '+str(outCNFFile)+' > '+outputFile
    startTime = time.time()
    os.system(cmd)
    endTime = time.time()

    writeStr = 'ExactCount:sharpSAT::'+str(endTime-startTime)+':0\n'
    f = open(logFile, 'a')
    f.write(writeStr)
    f.close()

    # Reading the output of sharpSAT
    f = open(outputFile, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        if (line.strip() == ''):
            continue
        if (line.strip()[0].isdigit()):
            unweightedCount = int(line.strip())
            break
    logweightedCount = math.log(unweightedCount, 2) - \
        (eqWtVars+totalVars-origTotalVars)
    print("The log weighted count is "+str(logweightedCount))
    print("The time taken is:"+str(endTime-startTime))
    print("The logs are printed in: "+str(logFile))

    cmd = 'rm '+str(outCNFFile)
    os.system(cmd)
    cmd = 'rm '+str(outputFile)
    os.system(cmd)
