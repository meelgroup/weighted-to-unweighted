# Weighted to unweighted formula converter
This tool makes an weighted formula into and unweighted formula, where it can later be counted or sampled using unweighted counters/samplers. The way this tool works is explained in detail in [this paper](https://www.comp.nus.edu.sg/~meel/Papers/ijcai15.pdf). Essentially, the variables with non-0.5 weights are attached a formula that approximates the weight.

### How to use ###
Let's say we have the following formula:

```
$ cat my.cnf
p cnf 2 1
c ind 1 2 0
1 2 0
w 1 0.9
w 2 0.5
```

We convert this weighted formula to an unweighted formula:

```
./weighted_to_unweighted.py my.cnf my-unweighted.cnf
Orig vars: 2       Added vars: 7
The resulting count you have to divide by: 2**7
```

Our resulting formula is correctly unweigthed:

```
$ cat my-unweighted.cnf
p cnf 9 9
c ind 1 2 3 4 5 6 7 8 9 0
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

we can now count this system using an unweighted counter, e.g. approxmc:

```
$ ./approxmc my-unweighted
[...]
[appmc] FINISHED AppMC T: 0.01 s
[appmc] Number of solutions is: 62*2**2

$ python
> 62*2**2/2**7
1.9375
```

So the weighted count is 1.937. We can also sample this system using an unweighted sampler, e.g. unigen:

```
$ ./unigen my-unweighted.cnf --sampleout samples --samples 1000 > /dev/null
$ cut -d " " -f 1-2 samples | sort | uniq -c
55  -1  2
478  1 -2
490  1  2

```

We sampled the system in a weighted way.

### Contributors ###
Kuldeep Meel (meel@comp.nus.edu.sg)
Mate Soos (soos.mate@gmail.com)
