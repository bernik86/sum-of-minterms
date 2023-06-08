#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 bernik86.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from itertools import product
import argparse
from typing import Optional
import string

Table = list[list[tuple[int, ...], int]]


class Gate:
    def __init__(self, expression: str):
        self.truth_table = []
        self.expression = normalize_bool_fct_str(expression.strip())
        self.output = 0

        if self.expression[0] in {"'", "*", "+", "!"}:
            raise ValueError(
                f"Expression or sub-expression cannot start with an operator: {expression}!"
            )

        if par_open := self.expression.count("("):
            par_closed = self.expression.count(")")
            if par_open != par_closed:
                raise ValueError("Unmatched paranthesis!")

            i_open, i_close = parse_outer_paranthesis(self.expression)

            len_expr = len(self.expression)
            if i_open == 0 and i_close == len_expr - 2:
                self.operator = "NOT"
                self.inp_1 = Gate(self.expression[1:-2])
                self.inp_2 = None
            elif i_open == 0 and i_close == len_expr - 1:
                self.operator = "UNITY"
                self.inp_1 = Gate(self.expression[1:-1])
                self.inp_2 = None
            else:
                split_at = i_open - 2 if i_open > 0 else i_close
                if self.expression[split_at + 1] in {"'", "!"}:
                    split_at += 1
                expr_1 = self.expression[: split_at + 1]
                expr_2 = self.expression[split_at + 1 :]

                match self.expression[split_at + 1]:
                    case "*":
                        self.operator = "AND"
                    case "+":
                        self.operator = "OR"
                    case _:
                        raise NotImplementedError("Unknown operator encountered!")

                self.inp_1 = Gate(expr_1) if expr_1 else None
                self.inp_2 = Gate(expr_2) if expr_2 else None
        elif self.expression.count("+"):
            expr = self.expression.split("+", maxsplit=1)
            self.operator = "OR"
            self.inp_1 = Gate(expr[0])
            self.inp_2 = Gate(expr[1])
        elif self.expression.count("*"):
            expr = self.expression.split("*", maxsplit=1)
            self.operator = "AND"
            self.inp_1 = Gate(expr[0])
            self.inp_2 = Gate(expr[1])
        elif not_ops := self.expression.count("'") + self.expression.count("!"):
            self.operator = "NOT" if not_ops % 2 != 0 else "UNITY"
            self.inp_1 = Gate(self.expression[0])
            self.inp_2 = None
        else:
            self.inp_1 = None
            self.inp_2 = None
            self.operator = "INPUT"

    def update(self, inputs: dict):
        '''
            Update the output of the gate.

            inputs: a dict containing True/1 and False/0 values for all
                    input variables.
        '''

        if self.inp_1 is not None:
            self.inp_1.update(inputs)

        if self.inp_2 is not None:
            self.inp_2.update(inputs)

        match self.operator:
            case "AND":
                self.output = self.inp_1.output and self.inp_2.output
            case "OR":
                self.output = self.inp_1.output or self.inp_2.output
            case "NOT":
                self.output = not self.inp_1.output
            case "INPUT":
                self.output = inputs[self.expression]
            case "UNITY":
                self.output = self.inp_1.output
            case _:
                raise NotImplementedError

    def print_truth_table(self):
        '''
            Print the truth table of Gate.
        '''

        if len(self.truth_table) == 0:
            generate_truth_table(self)

        input_symbols = extract_input_symbols(self.expression)
        print_truth_table(self.truth_table, input_symbols)

    def print_sum_of_minterms(self):
        '''
            Prints the canonical sum of minterms form of the boolean expression.
        '''

        print(sum_of_min_terms(self))


def parse_outer_paranthesis(expr: str) -> (int, int):
    '''
        Determines positions of the outermost opening and closing paranthesis.

        expr: string that is parsed.

        Returns tuple of integers representing the positions of the opening
        and closing paranthesis.
    '''

    i_open = -1
    i_close = -1
    count = 0
    for i, sym in enumerate(expr):
        if sym == "(":
            if count == 0:
                i_open = i
            count += 1
        if sym == ")":
            count -= 1
            if count == 0:
                i_close = i
                break
            if i_open == -1:
                raise ValueError("Invalid Paranthesis")

    return i_open, i_close


def extract_input_symbols(fct_str: str) -> list[str]:
    '''
        Get list of variables in boolean expression in reversed alphabetical order.

        fct_str: string representing boolean expression.

        Returns list of input symbols.
    '''

    input_symbols = {sym for sym in fct_str if sym.isalpha()}
    input_symbols = sorted(list(input_symbols), reverse=True)

    return input_symbols


def generate_truth_table(circuit: Gate):
    '''
        Build up the truth table for a given logical circuit/Gate.

        circuit: logical circuit/Gate for which truth table is generated.
    '''

    fct_str = circuit.expression
    input_symbols = extract_input_symbols(fct_str)
    n_sym = len(input_symbols)
    table = []

    for inp in product([0, 1], repeat=n_sym):
        inputs = dict(zip(input_symbols, inp))
        circuit.update(inputs)
        table.append([inp, normalize_bool(circuit.output)])

    circuit.truth_table = table


def read_table_from_file(filename: str) -> Table:
    '''
        Read truth table from file. The file needs to contain one column for
        each input variable and one for the output variable. No comments or
        empty lines are supported yet.

        Example:
        0 0 1
        0 1 0
        1 0 0
        1 1 1

        filename: path to file which contains truth table.

        Returns the truth table as list[list[tuple[int, ...], int]]
    '''

    with open(filename, "r", encoding="utf-8") as table_file:
        lines = table_file.readlines()

    def parse_line(line: str) -> list[tuple[int], int]:
        line = line.strip().split()
        inp = tuple(int(i) for i in line[:-1])
        out = int(line[-1])
        return [inp, out]

    line_1 = parse_line(lines[0])
    n_inp = len(line_1[0])

    if len(lines) < 2**n_inp:
        raise ValueError("Table incomplete!")
    if len(lines) > 2**n_inp:
        raise ValueError("Table overdefined!")

    table = []
    table.append(line_1)

    for line in lines[1:]:
        table.append(parse_line(line))

    check_table(table, n_inp)

    return table


def check_table(table: Table, n_inp: int):
    '''
        Checks whether the inputs of a given truth table are valid
        (correct amount and order of 0s and 1s).

        Raises a ValueError if truth table is inconsistent.

        table: truth table to be checked.
        n_inp: number of input variables (TODO: automatically determine n_inp).
    '''

    for i, inp in enumerate(product([0, 1], repeat=n_inp)):
        table_inp = table[i][0]

        if table_inp != inp:
            raise ValueError(
                f"Error: Truth table has wrong input values in line {i + 1}"
            )


def print_truth_table(table: Table, input_symbols: Optional[list[str]]):
    '''
        Print formatted truth table to terminal.

        table: table to print to terminal.
        input_symbols: list of letters to use as names for inputs [optional]
    '''

    if input_symbols is None:
        n_sym = len(table[0][0])
        input_symbols = list(string.ascii_uppercase[:n_sym])[::-1]
    else:
        n_sym = len(input_symbols)

    truth_table = [
        "\t".join(input_symbols) + "\t | F",
        "--------" * (n_sym + 1),
    ]

    for line in table:
        row = "\t".join(map(str, line[0])) + "\t | " + str(line[1])
        truth_table.append(row)

    print("\n".join(truth_table))


def sum_of_min_terms(circuit: Gate) -> str:
    '''
        Create string of canonical sum of minterms form of logical expression.

        circuit: logical circuit/Gate for which the canoncical form is created.

        Returns string of the canonical form as "F = <sum-of-minterms>"
    '''

    if len(circuit.truth_table) == 0:
        generate_truth_table(circuit)

    input_symbols = extract_input_symbols(circuit.expression)

    min_terms = build_minterms(circuit.truth_table, input_symbols)

    return "F = " + min_terms


def build_minterms(table: Table, input_symbols: Optional[list[str]]) -> str:
    '''
        Determines canonical sum of minterms form from the truth table of a
        boolean expression and returns it as string.

        Returns string containing only the canonical form (without any formatting
        sugar).
    '''

    if input_symbols is None:
        n_sym = len(table[0][0])
        input_symbols = list(string.ascii_uppercase[:n_sym])[::-1]

    min_terms = []

    for line in table:
        if line[1]:
            inp = line[0]
            row = [
                input_symbols[i] if inp[i] else input_symbols[i] + "'"
                for i in range(len(inp))
            ]
            min_terms.append("".join(row))

    min_terms = min_terms[::-1]
    min_terms = " + ".join(min_terms)

    return min_terms


def normalize_bool(value: bool) -> int:
    '''
        Convert bool (True/False) to int (0/1).

        value: bool value to convert.

        Returns 0 or 1 depending on value.
    '''

    match value:
        case True:
            return 1
        case False:
            return 0
        case _:
            return value


def normalize_bool_fct_str(fct_str: str) -> str:
    '''
        Clean the raw form of the boolean expression given by the user.
        Removes spaces, escape characters, etc. and inserts AND operator
        where needed.

        fct_str: string containing the raw form of the boolean expression.

        Returns cleaned up string of boolean expression.
    '''

    fct_str = (
        fct_str.upper()
        .replace(" ", "")
        .replace("\\", "")
        .replace("!", "'")
        .strip("*")
        .strip("+")
    )
    pos = []
    for i in range(len(fct_str) - 1):
        sym_i = fct_str[i]
        sym_i1 = fct_str[i + 1]

        if (sym_i.isalpha() or sym_i == "'") and (sym_i1.isalpha() or sym_i1 == "("):
            pos.append(i)
        elif sym_i == ")" and sym_i1.isalpha():
            pos.append(i)

    for i in reversed(pos):
        fct_str = fct_str[: i + 1] + "*" + fct_str[i + 1 :]

    return fct_str


def main(args):
    parser = argparse.ArgumentParser()

    parser.add_argument("-F", "--function", help="Boolean function or expression")
    parser.add_argument(
        "-t",
        "--table",
        action="store_true",
        help="Print truth table for boolean function",
    )
    parser.add_argument(
        "-r",
        "--read-table",
        help="Read truth table from file and print sum of minterms",
    )
    args = parser.parse_args()

    if args.function is not None:
        circuit = Gate(args.function)
        print("Boolean function raw input: F = ", args.function.strip())
        print("Boolean function normalized: F = ", circuit.expression)
        print("Canonical form of F in sum-of-minterms notation:")
        circuit.print_sum_of_minterms()

        if args.table:
            print("Truth Table:")
            circuit.print_truth_table()

    elif args.read_table is not None:
        print("Reading truth table...")
        table = read_table_from_file(args.read_table)
        min_terms = build_minterms(table, None)
        print("Canonical form of F in sum-of-minterms notation:")
        print("F = " + min_terms)

        if args.table:
            print("Truth Table:")
            print_truth_table(table, None)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
