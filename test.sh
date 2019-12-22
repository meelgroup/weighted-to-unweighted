#!/usr/bin/bash
set -e
#set -x

APPMC="/home/soos/development/sat_solvers/scalmc/build/approxmc"

echo "Doing NO IND"
rm -f b.cnf
rm -f x
./weighted_to_unweighted.py --prec 4 CNFs/a-no-ind.cnf b.cnf
${APPMC} b.cnf --sampleout x --samples 1000 > /dev/null
cut -d " " -f 1-2 x | sort | uniq -c

echo "-------------"
echo "Doing IND"
rm -f b.cnf
rm -f x
./weighted_to_unweighted.py --prec 4 CNFs/a-with-ind.cnf b.cnf
${APPMC} b.cnf --sampleout x --samples 1000 > /dev/null
cut -d " " -f 1-2 x | sort | uniq -c

