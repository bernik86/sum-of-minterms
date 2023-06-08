# sum-of-minterms
Python script that calculates the canonical form of a boolean expression (see https://en.wikipedia.org/wiki/Canonical_normal_form).

## Requirement

Python >= 3.10

## Usage

Specify the boolean function using the `-F` parameter. The expression should be enclosed in " and can use letters (each letter will be interpreted as one variable in the expression) and the following symbols: 
 - `*`: AND (can be omitted)
 - `+`: OR 
 - `'`: NOT
 - `(` and `)` to group sub-expressions

The parameter `-t` can be used to generate and print the truth table of the expression, and `-r` generates the canonical form from a truth table read from file.

### Examples:

`python sum_of_minterms.py -F "A*B+C"`

Output:

```
Boolean function raw input: F =  A*B+C
Boolean function normalized: F =  A*B+C
Canonical form of F in sum-of-minterms notation:
F = CBA + CBA' + CB'A + CB'A' + C'BA
```

`python sum_of_minterms.py -F "A*B+C" -t`

Output:

```
Boolean function raw input: F =  A*B+C
Boolean function normalized: F =  A*B+C
Canonical form of F in sum-of-minterms notation:
F = CBA + CBA' + CB'A + CB'A' + C'BA
Truth Table:
C	B	A	 | F
--------------------------------
0	0	0	 | 0
0	0	1	 | 0
0	1	0	 | 0
0	1	1	 | 1
1	0	0	 | 1
1	0	1	 | 1
1	1	0	 | 1
1	1	1	 | 1
```

File format for truth table:
The table consists of n columns for n-1 inputs and 1 output variable (no comments or empty lines are recognized at this point).

Example:
```
0 0 1
0 1 0
1 0 0
1 1 1
```

Reading this table from file using `python sum_of_min_terms.py -r table` leads to the following output:

```
Reading truth table...
Canonical form of F in sum-of-minterms notation:
F = BA + B'A'
```

