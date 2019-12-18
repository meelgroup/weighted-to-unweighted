#!/usr/bin/bash

echo "Doing NO IND"
./weightcount.py --prec 4 CNFs/a-no-ind.cnf b.cnf
~/development/sat_solvers/scalmc/build/approxmc b.cnf --sampleout x --samples 1000 > /dev/null
cut -d " " -f 1-2 x | sort | uniq -c

echo "-------------"
echo "Doing IND"
./weightcount.py --prec 4 CNFs/a-with-ind.cnf b.cnf
~/development/sat_solvers/scalmc/build/approxmc b.cnf --sampleout x --samples 1000 > /dev/null
cut -d " " -f 1-2 x | sort | uniq -c

