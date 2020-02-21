# Import libraries
import argparse
import sys
import timeit
import statistics
import time
import matplotlib.pyplot as plt
# get important methods from the sudoku file
from sudoku import Board, find_one_solution, count_number_solutions


def parse_arguments(argv):
    parser = argparse.ArgumentParser(description='Benchmark your Sudoku solver.')
    parser.add_argument('benchmark', help="Path to the benchmark file with all benchmark instances.")
    parser.add_argument('-n', default=10, type=int, help="Max. number of boards from the benchmark file to test.")
    
    # adding repeatitively argument to the parser in order to parse large number of instances
    parser.add_argument('-rn',default=0, type=int, help="Max. number of boards from the benchmark file to test repeatedly.")
    
    return parser.parse_args(argv)


def read_benchmark_file(file):
    with open(file, 'r') as f:
        for line in f:
            yield line.rstrip('\n')


def main(argv):
    # Parsing aruments
    args = parse_arguments(argv)
    # cpu time calculations
    times = []
    cpu_time = []
    # number of calculations
    n_list=[]
    # defining step-size
    n=10
    # if using "--rn" command - Repeatitively n
    if(args.rn !=0):
        # iterate each an increasing n=10 while it's smaller than the defined n in cmd/bash 
        while n <= args.rn:
            # read benchmark file and get the arguments
            for i, board in enumerate(read_benchmark_file(args.benchmark), start=1):
                # append the cpu time for each solution finding for a board
                times.append(timeit.timeit(lambda: find_one_solution(Board(board), verbose=False), number=1))
                # continue for the next puzzle by break
                if i == args.n:
                    break
            # apeending cpu time for each iteration
            cpu_time.append(sum(times))
            # appending n number of calculation
            n_list.append(n)
            # printing summary information 
            print(f"Runs: {n}, Total time (sec): {sum(times):.3f}, Max: {max(times):.3f},"
                  f" Min: {min(times):.3f}, Avg: {statistics.mean(times):.3f}, stdev: {statistics.stdev(times):.3f}")
            n=n+10
        # plot cpu time as a function of n
        plt.plot(n_list,cpu_time)
        plt.title("CPU TIME")
        # save plot
        plt.savefig("CPU_TIME"+str(len)+".png")
        # initialize cpu times
        times=[]
        
    # if using "--n" command - NOT! Repeatitively n
    else:
        for i, board in enumerate(read_benchmark_file(args.benchmark), start=1):
            # appending cpu time 
            times.append(timeit.timeit(lambda: find_one_solution(Board(board), verbose=False), number=1))
            # continue for the next puzzle by break
            if i == args.n:
                break
         # printing summary information 
         print(f"Runs: {args.n}, Total time (sec): {sum(times):.3f}, Max: {max(times):.3f},"
                 f" Min: {min(times):.3f}, Avg: {statistics.mean(times):.3f}, stdev: {statistics.stdev(times):.3f}")
         
    
    
    
    times = []
    cpu_time = []
    cpu_time_all = []
    n_list=[]
    n=10 
    
    """
    
    if(args.rn !=0):
         n_list=[]
         for i, board in enumerate(read_benchmark_file(args.benchmark), start=1):
             times.append(timeit.timeit(lambda: count_number_solutions(Board(board), verbose=False), number=1))
             n_list.append(i)
             if i == args.n:
                break
         print(f"All Solutions Runs: {args.n}, Total time (sec): {sum(times):.3f}, Max: {max(times):.3f},"
                 f" Min: {min(times):.3f}, Avg: {statistics.mean(times):.3f}, stdev: {statistics.stdev(times):.3f}")
        
         plt.plot(n_list,times)
         plt.title("CPU TIME")
        #plt.xlim(min(n_list), max(n_list))
        #plt.show()
         plt.savefig("CPU_TIME_ALL.png")
         times=[]
         
     """

if __name__ == "__main__":
    main(sys.argv[1:])
