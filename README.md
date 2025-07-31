# Weighted to unweighted formula converter
This tool makes an weighted formula into and unweighted formula, where it can
later be counted or sampled using unweighted counters/samplers. The way this
tool works is explained in detail in [this
paper](https://www.comp.nus.edu.sg/~meel/Papers/ijcai15.pdf). Essentially, the
variables with non-default weights are attached a formula that approximates the
weight.

## How to use
Let's say we have the following formula in the Model Counting Competition [DIMACS-like
format](https://mccompetition.org/assets/files/2021/competition2021.pdf):
```
$ cat weighted.cnf
p cnf 2 1
c t wpmc
c p show 1 2 0
1 2 0
c p weight 1 0.9 0
c p weight 2 0.5 0
```

First, we _must_ use [Arjun](https://github.com/meelgroup/arjun) to simplify
the formula:
```
./arjun weighted.cnf simplified.cnf
```

Now we can convert this weighted formula to an unweighted formula:
```
./weighted_to_unweighted.py simplified.cnf unweighted.cnf
```
Header says vars: 2  maximum var used: 2
Orig vars: 2       Added vars: 7
The resulting count you have to divide by: 2**8
Time to transform: 0.000 s
```

Our resulting formula is correctly unweighted:
```
$ cat unweighted.cnf
p cnf 9 9
c p show 1 2 3 4 5 6 7 8 9 0
1 2 0
9 8 5 4 3 -1 0
7 5 4 3 -1 0
6 5 4 3 -1 0
9 -7 -6 1 0
-8 -7 -6 1 0
-5 1 0
-4 1 0
-3 1 0
```

we can now count this system using an unweighted counter, e.g.
[ApproxMC](https://github.com/meelgroup/approxmc/):
```
$ ./approxmc unweighted.cnf
[...]
c [appmc] Number of solutions is: 61*2**2
s SATISFIABLE
s mc 244

$ python
>>> 244/(2.0**8)
0.953125
```

## Authors
Kuldeep Meel (meel@comp.nus.edu.sg)
Mate Soos (soos.mate@gmail.com)
