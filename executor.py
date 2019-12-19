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


cmd = './doalarm -t real ' + \
    str(timeout)+' ./sharpSAT -q -c 3000 '+str(args.outputFile)+' > tmp_timing'
startTime = time.time()
os.system(cmd)

writeStr = 'ExactCount:sharpSAT::'+str(time.time()-startTime)+':0\n'
f = open(logFile, 'a')
f.write(writeStr)
f.close()

# Reading the output of sharpSAT
f = open("tmp_timing", 'r')
lines = f.readlines()
f.close()
for line in lines:
    if line.strip() == '':
        continue
    if line.strip()[0].isdigit():
        unweightedCount = int(line.strip())
        break
logweightedCount = math.log(unweightedCount, 2) - \
    (eqWtVars+totalVars-origTotalVars)
print("The log weighted count is "+str(logweightedCount))
print("The time taken is:", time.time()-startTime)
print("The logs are printed in: ", logFile)
