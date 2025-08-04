#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2020 Kuldeep S Meel, Mate Soos
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

import time
import argparse
import decimal
import re


class RetVal:
    def __init__(self, origVars, origCls, vars, totalCount, div):
        self.origVars = origVars
        self.origCls = origCls
        self.vars = vars
        self.totalCount = totalCount
        self.div = div


class Converter:
    def __init__(self, precision, verbose=False):
        self.precision = precision
        self.verbose = verbose
        self.sampl_set = {}

    def pushVar(self, var, cnfClauses):
        cnfLen = len(cnfClauses)
        for i in range(cnfLen):
            cnfClauses[i].append(var)
        return cnfClauses

    def getCNF(self, var, binStr, sign, origVars):
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
        self.pushVar(var, cnfClauses)
        return cnfClauses

    def encodeCNF(self, var,  bit_mult, bit_prec, num_vars, num_cls, div):
        # exactly half, i.e. 0.5
        if bit_prec == 1 and bit_mult == 1:
            return "", num_vars, num_cls, div+1

        if bit_prec == 0:
            print("ERROR: the formula was not preprocessed by Arjun")
            exit(-1)

        self.sampl_set[num_vars+1] = 1
        binStr = str(bin(int(bit_mult)))[2:-1]
        binLen = len(binStr)
        for i in range(bit_prec-binLen-1):
            binStr = '0'+binStr
        for i in range(bit_prec-1):
            self.sampl_set[num_vars+i+2] = 1
        complementStr = ''
        for i in range(len(binStr)):
            if binStr[i] == '0':
                complementStr += '1'
            else:
                complementStr += '0'
        origCNFClauses = self.getCNF(-var, binStr, True, num_vars)

        writeLines = ''
        for i in range(len(origCNFClauses)):
            num_cls += 1
            for j in range(len(origCNFClauses[i])):
                writeLines += str(origCNFClauses[i][j])+' '
            writeLines += '0\n'

        cnfClauses = self.getCNF(var, complementStr, False, num_vars)
        for i in range(len(cnfClauses)):
            if cnfClauses[i] in origCNFClauses:
                continue
            num_cls += 1
            for j in range(len(cnfClauses[i])):
                writeLines += str(cnfClauses[i][j])+' '
            writeLines += '0\n'

        vars = num_vars+bit_prec
        return writeLines, vars, num_cls, div+bit_prec

    # return (weight:bits ratio, number of bits needed to represent the weight)
    def quantize_weight(self, init_w):
        assert type(init_w) == decimal.Decimal

        assert self.precision > 1, "Precision must be at least 2"
        if init_w < decimal.Decimal(0.0) or init_w > decimal.Decimal(1.0):
            print(f"ERROR: Weight {init_w} is not in the range [0.0, 1.0]")
            exit(-1)

        if self.verbose:
            print(f"Query for weight {init_w}")

        weight = init_w*pow(2, self.precision)
        weight = weight.quantize(decimal.Decimal("1"))
        weight = int(weight)
        prec = self.precision
        if self.verbose:
            print(f"Weight {weight} prec {prec}. Generated from {init_w} * 2^{self.precision}")

        while weight % 2 == 0 and prec > 0:
            weight = weight/2
            prec -= 1

        if self.verbose:
            print(f"for input weight {init_w} returning: weight: {weight} prec: {prec}")

        return weight, prec

    def delete_1_1_weights(self, w, vars):
        # delete 1/1 weights
        vars2 = {}
        for var in vars.keys():
            if w[var] == decimal.Decimal("1") and w[-var] == decimal.Decimal("1"):
                del w[var]
                del w[-var]
            else:
                vars2[var] = 1
        return vars2, w


    # make them all add up to 1
    def normalize_weights(self, vars, w):
        w2 = {}
        mult = decimal.Decimal("1")
        for var in vars.keys():
            total = w[var] + w[-var]
            if total == decimal.Decimal("1"):
                w2[var] = w[var]
                w2[-var] = w[-var]
            else:
                diff = decimal.Decimal("1")/total
                mult *= total
                w2[var] = w[var]*diff
                w2[-var] = w[-var]*diff

        return w2, mult


    def check_all_weights_non_zero_or_negativer(self, w):
        for lit,weight in w.items():
            if weight == decimal.Decimal("0"):
                print(f"ERROR: Literal {lit} has a (forced) weight of 0, which means the CNF has not been preprocessed by Arjun. Exiting.")
                exit(-1)
            if weight < decimal.Decimal("0"):
                print(f"ERROR: Literal {lit} has a (forced) weight that's negative: {weight}. This is not allowed.")
                exit(-1)


    # returns multiplier
    def clean_up_weights(self, w):
        # make sure both var and -var are present
        toadd = []
        for lit,weight in w.items():
            if -lit not in w:
                toadd.append((-lit, decimal.Decimal("1")-weight))
        for lit,weight in toadd:
            w[lit] = weight
        del toadd

        self.check_all_weights_non_zero_or_negativer(w)

        vars = {}
        for lit,_ in w.items():
            vars[abs(lit)] = 1

        if self.verbose:
            print(f"found {len(vars)} variables with weights")
            for var in vars.keys():
                print(f"Variable {var} has weight {w[var]} and {-var} has weight {w[-var]}")

        vars, w = self.delete_1_1_weights(w, vars)
        w, mult = self.normalize_weights(vars, w)
        vars, w = self.delete_1_1_weights(w, vars)

        if self.verbose:
            print(f"After normalization to total 1 weights multiplier is {mult} and weights are:")
            for var in vars:
                print(f"Variable {var} has weight {w[var]} and {-var} has weight {w[-var]}")

        return mult, w

    #  The code is straightforward chain formula implementation
    def transform(self, lines, outputFile):
        orig_cnf_lines = ''
        vars = 0
        num_cls = 0
        div = 0
        origVars = 0
        origCls = 0
        maxvar = 0
        found_sampl_set = False
        found_header = False
        multiplier = None
        for line in lines:
            line = line.strip()
            line = re.sub(r'\s+', ' ', line)

            if len(line) == 0:
                print("ERROR: The CNF contains an empty line.")
                print("ERROR: Empty lines are NOT part of the DIMACS specification")
                print("ERROR: Remove the empty line so we can parse the CNF")
                exit(-1)

            if line[:2] == 'p ':
                fields = line.split()
                if (len(fields) != 4 or fields[1] != 'cnf'):
                    print("ERROR: The CNF header must be of the form 'p cnf VARS CLAUSES'")
                    exit(-1)
                vars = int(fields[2])
                num_cls = int(fields[3])
                origVars = vars
                origCls = num_cls
                found_header = True
                continue

            # parse independent set
            if line[:8] == "c p show" or line[:5] == "c ind":
                if line[:8] == "c p show": start = 8
                else: start = 5
                found_sampl_set = True
                for var in line[start:].split():
                    var = var.strip()
                    var = int(var)
                    if var == 0:
                        break
                    if var <= 0:
                        print(f"ERROR: The sampling set contains {var} but sampling vars must be positive")
                        exit(-1)
                    if var > vars:
                        print(f"ERROR: The sampling set contains {var} but header says we only have {vars} vars")
                        exit(-1)
                    self.sampl_set[var] = 1
                continue

            if "c MUST MULTIPLY BY" in line:
                if multiplier is not None:
                    print(f"ERROR: The CNF already has a multiplier defined: {multiplier}")
                    print("ERROR: Please remove the previous multiplier or the new one")
                    exit(-1)
                multiplier = self.parse_weight(line.split()[4])
                continue

            if line[0] == 'c' and line[:4] != 'c t ' and line[:4] != 'c p ':
                orig_cnf_lines += str(line + '\n')
                continue

            if not found_header:
                print("ERROR: The 'p cnf VARS CLAUSES' header must be at the top of the CNF!")
                exit(-1)

            # an actual clause
            if line[0].isdigit() or line[0] == '-':
                for lit in line.split():
                    maxvar = max(abs(int(lit)), maxvar)
                if len(line.split()) == 2:
                    print("ERROR: The CNF contains a clause with only one literal. This means Arjun has not been run. Exiting.")
                    exit(-1)
                orig_cnf_lines += str(line + '\n')

            # NOTE: we are skipping all the other types of things in the CNF
            #       for example, the weights
            continue

        if multiplier is None:
            multiplier = decimal.Decimal('1')

        if maxvar > vars:
            print(f"ERROR: CNF contains var {maxvar} but header says we only have {vars} vars")
            exit(-1)

        print(f"Header says vars: {vars}  maximum var used: {maxvar}")

        if not found_header:
            print("ERROR: No header 'p cnf VARS CLAUSES' found in the CNF!")
            exit(-1)

        # if "c ind" was not found, then all variables are in the sampling set
        if not found_sampl_set:
            print("WARNING: No sampling set found, assuming all variables are in the sampling set")
            for i in range(1, vars+1):
                self.sampl_set[i] = 1

        # weight parsing and CNF generation
        w = {}
        new_cnf = ''
        for line in lines:
            line = line.strip()
            line = re.sub(r'\s+', ' ', line)

            if line[:2] == 'w ' or line[:10] == 'c p weight':
                if line[:2] == 'w ': start = 2
                else: start = 10
                fields = line[start:].split()
                lit = int(fields[0])
                if abs(lit) > vars:
                    print(f"ERROR: Literal {lit} has a weight but it is not part of the CNF")
                    print(f"ERROR: The CNF only has {vars} variables, but literal {lit} is used")
                    exit(-1)
                val = self.parse_weight(fields[1])

                if lit == 0:
                    print("ERROR: Literal 0 has a weight, but literal 0 is not allowed in CNF")
                    exit(-1)

                # already has been declared, error
                if lit in w:
                    print(f"ERROR: Lit {lit} has TWO weights declared")
                    print("ERROR: You must ONLY declare each literal's weight ONCE")
                    exit(-1)
                var = abs(lit)

                # Model Counting Competition has these. I can't explain this without going on a rant
                if var not in self.sampl_set:
                    print(f"WARNING: Variable {var} has a weight but is not part of the sampling set. Skipping it!")
                    continue
                if w == decimal.Decimal("0"):
                    print(f"ERROR: Literal {lit} has a weight of 0, which means the CNF has not been preprocessed by Arjun. Exiting.")
                    exit(-1)

                w[lit] = val

        mult, w2 = self.clean_up_weights(w)
        multiplier *= mult

        for lit,val in w2.items():
            if lit < 0:
                # they now add up to 1, so we can skip the negative literals
                continue
            var = abs(lit)
            bit_mult, bit_prec = self.quantize_weight(val)

            if self.verbose:
                new_weight = decimal.Decimal(bit_mult)/decimal.Decimal(2**bit_prec)
                print(f"var: {var} orig-weight: {val} bit_mult: {bit_mult} bit_prec: {bit_prec} weight as represented in CNF: {new_weight}")

            # we have to encode to CNF the translation
            lines, vars, num_cls, div = self.encodeCNF(var, bit_mult, bit_prec, vars, num_cls, div)
            new_cnf += lines

        with open(outputFile, 'w') as f:
            f.write('p cnf '+str(vars)+' '+str(num_cls)+' \n')
            f.write('c p show ')
            for k in self.sampl_set:
                f.write("%d " % k)
            f.write("0\n")

            f.write(orig_cnf_lines)
            f.write(new_cnf)
            f.write('c MUST MULTIPLY BY %s 0\n' % multiplier)

        return RetVal(origVars, origCls, vars, num_cls, div)

    def parse_weight(self, dat):
        if "/" in dat:
            f = dat.split('/')
            val = decimal.Decimal(f[0]) / decimal.Decimal(f[1])
        else:
            val = decimal.Decimal(dat)

        return val


# main function
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

    decimal.getcontext().prec = 100

    startTime = time.time()
    c = Converter(precision=args.prec, verbose=args.verbose)

    # read in input CNF
    with open(args.inputFile, 'r') as f:
        lines = f.readlines()

    ret = c.transform(lines, args.outputFile)

    print("Orig vars: %-7d Added vars: %-7d" % (ret.origVars, ret.vars-ret.origVars))
    print("The resulting count you have to divide by: 2**%d" % ret.div)
    print("Time to transform: %0.3f s" % (time.time()-startTime))
    exit(0)
