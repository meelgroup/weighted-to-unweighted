# Weighted to unweighted formula converter
This tool makes an weighted formula into and unweighted formula, where it can later be counted or sampled using unweighted counters/samplers. The way this tool works is explained in detail in [this paper](https://www.comp.nus.edu.sg/~meel/Papers/ijcai15.pdf). Essentially, the variables with non-0.5 weights are attached a formula that approximates the weight.

### How to use ###
Let's say we have the following formula:

```
$ cat my.cnf
p cnf 2 0
w 1 0.9
w 2 0.5
```

We now run our system:

```
./weighted_to_unweighted.py my.cnf my-unweighted.cnf
Header says vars: 2  maximum var used: 0
Orig vars: 2       New Vars: 9
Time to transform: 0.000 s
```

Our resulting formula is unweigthed:

```
$ cat my-unweighted.cnf
p cnf 9 8
c ind 1 2 3 4 5 6 7 8 9 0
9 8 5 4 3 -1 0
7 5 4 3 -1 0
6 5 4 3 -1 0
9 -7 -6 1 0
-8 -7 -6 1 0
-5 1 0
-4 1 0
-3 1 0
```

We can now sample this system using an unweighted sampler, e.g. unigen:

```
$ ./unigen my-unweighted.cnf --sampleout samples --samples 1000 > /dev/null
$ cut -d " " -f 1-2 samples | sort | uniq -c
     76 -1 -2
     66 -1 2
    436 1 -2
    438 1 2
```

Hence, we sampled the system in a weighted way.

### Contributors ###
Kuldeep Meel (meel@comp.nus.edu.sg)
Mate Soos (soos.mate@gmail.com)
