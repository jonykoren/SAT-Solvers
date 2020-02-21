#!/usr/bin/env python3

import argparse
import itertools
import math
import sys

from utils import save_dimacs_cnf, solve


def parse_arguments(argv):
    parser = argparse.ArgumentParser(description='Solve Sudoku problems.')
    parser.add_argument("board", help="A string encoding the Sudoku board, with all rows concatenated,"
                                      " and 0s where no number has been placed yet.")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Do not print any output.')
    parser.add_argument('-c', '--count', action='store_true',
                        help='Count the number of solutions.')
    return parser.parse_args(argv)


def print_solution(solution):
    """ Print a (hopefully solved) Sudoku board represented as a list of 81 integers in visual form. """

    print(f'Solution: {"".join(map(str, solution))}')
    print('Solution in board form:')
    Board(solution).print()


def compute_solution(sat_assignment, variables, size):
    solution = []
    # TODO: Map the SAT assignment back into a Sudoku solution

    # Find solution according to sat_assignment(CNF)
    for key, value in sat_assignment.items():
          if(value):
              result = variables.get(key)
              solution.append((result))
    return solution
   
    # A function to calculate the 's(x,y,z)' value
def s(x, y, z):
    return 81 * (x - 1) + 9 * (y - 1) + z

 
def generate_theory(board, verbose):
    """ Generate the propositional theory that corresponds to the given board. """

    # Initiate variables and data structures
    preassigned_entries = []
    row_number = 1
    column_number = 0
    size = board.size()
    clauses = []
    variables = {}
    listed=[]

    # Assign values into variables dictionary
    count = 1
    for i in range(1,(size*size)+1):
        for j in range(1,(size+1)):
            variables.update({count:j})
            count=count+1

    # Read initial board entries and format
    boardString = ''.join(str(e) for e in board.data)
    k =[boardString[i:i+size] for i in range(0, len(boardString), size)]

    for j in range(0, size):
        digits = k[j]
        column_number = 0
        for digit in digits:
            column_number += 1
            if digit != "0":
                preassigned_entries.append(
                    s(row_number, column_number, int(digit))
                )
        row_number += 1

    # Initiate preassigned entries to the board
    for entry in preassigned_entries:
        clauses.append([entry])
    
    # Constraint 1) There is at least one number in each entry
    for x in range(1, 10):
        for y in range(1, 10):
            for z in range(1, 10):
                listed.append(s(x, y, z))
            clauses.append(listed)
            listed=[]
    # Constraint 2) Each number appears at most once in each row
    for y in range(1, 10):
        for z in range(1, 10):
            for x in range(1, 9):
                for i in range(x + 1, 10):
                    listed = [-s(x, y, z), -s(i, y, z)]
                    clauses.append(listed)
    # Constraint 3) Each number appears at most once in each column
    for x in range(1, 10):
        for z in range(1, 10):
            for y in range(1, 9):
                for i in range(y + 1, 10):
                    listed = [-s(x, y, z), -s(x, i, z)]
                    clauses.append(listed)
    # Constraint 4a )Each number appears at most once in each 3x3 subgrid row
    for z in range(1, 10):
        for i in range(0, 3):
            for j in range(0, 3):
                for x in range(1, 4):
                    for y in range(1, 4):
                        for k in range(y + 1, 4):
                            listed = [-s(3 * i + x, 3 * j + y, z), -s(3 * i + x, 3 * j + k, z)]
                            clauses.append(listed)
    # Constraint 4a )Each number appears at most once in each 3x3 subgrid column
    for z in range(1, 10):
        for i in range(0, 3):
            for j in range(0, 3):
                for x in range(1, 4):
                    for y in range(1, 4):
                        for k in range(x + 1, 4):
                            for l in range(1, 4):
                                listed = [-s(3 * i + x, 3 * j + y, z), -s(3 * i + k, 3 * j + l, z)]
                                clauses.append(listed)
    # TODO
    return clauses, variables, size


def count_number_solutions(board, verbose=False):
    size = board.size()
    solutionArray=[]


    # Check if there is a satisfiable solution for given variables and record
    for i in range(0,(size*size)):
         if(board.data[i]==0):
              for j in range(1,size+1):
                  board.data[i]=j
                  solution = find_one_solution(board,verbose)
                  if(solution is not None):
                      solutionArray.append(solution)
              board.data[i]=0
                    

    # Count satisfiable solutions
    solutionArray = [i for n, i in enumerate(solutionArray) if i not in solutionArray[n + 1:]]
    count = len(solutionArray)
    print(f'Number of solutions: {count}')

    # TODO

def find_one_solution(board, verbose=False):
    clauses, variables, size = generate_theory(board, verbose)
    return solve_sat_problem(clauses, "theory.cnf", size, variables, verbose)


def solve_sat_problem(clauses, filename, size, variables, verbose):
    save_dimacs_cnf(variables, clauses, filename, verbose)
    result, sat_assignment = solve(filename, verbose)
    if result != "SAT":
        if verbose:
            print("The given board is not solvable")
        return None
    solution = compute_solution(sat_assignment, variables, size)
    if verbose:
        print_solution(solution)
    return sat_assignment


class Board(object):
    """ A Sudoku board of size 9x9, possibly with some pre-filled values. """
    def __init__(self, string):
        """ Create a Board object from a single-string representation with 81 chars in the .[1-9]
         range, where a char '.' means that the position is empty, and a digit in [1-9] means that
         the position is pre-filled with that value. """
        size = math.sqrt(len(string))
        if not size.is_integer():
            raise RuntimeError(f'The specified board has length {len(string)} and does not seem to be square')
        self.data = [0 if x == '.' else int(x) for x in string]
        self.size_ = int(size)

    def size(self):
        """ Return the size of the board, e.g. 9 if the board is a 9x9 board. """
        return self.size_

    def value(self, x, y):
        """ Return the number at row x and column y, or a zero if no number is initially assigned to
         that position. """
        return self.data[x*self.size_ + y]

    def all_coordinates(self):
        """ Return all possible coordinates in the board. """
        return ((x, y) for x, y in itertools.product(range(self.size_), repeat=2))

    def print(self):
        """ Print the board in "matrix" form. """
        assert self.size_ == 9
        for i in range(self.size_):
            base = i * self.size_
            row = self.data[base:base + 3] + ['|'] + self.data[base + 3:base + 6] + ['|'] + self.data[base + 6:base + 9]
            print(" ".join(map(str, row)))
            if (i + 1) % 3 == 0:
                print("")  # Just an empty line


def main(argv):
    args = parse_arguments(argv)
    board = Board(args.board)

    if args.count:
        count_number_solutions(board, verbose=False)
    else:
        find_one_solution(board, verbose=not args.quiet)


if __name__ == "__main__":
    main(sys.argv[1:])
