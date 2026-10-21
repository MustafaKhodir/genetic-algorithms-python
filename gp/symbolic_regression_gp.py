#!/usr/bin/env python3
# Symbolic regression with genetic programming, using DEAP.
#
# GP evolves a maths expression f(x) as a tree of operators (add, sub, mul,
# protected div, neg, sin, cos) and constants until it fits a set of sample
# points from a target function. Three targets to pick from:
#   1. 5x^5 + 4x^4 + 3x^3 + 2x^2 + x
#   2. 4 sin(5 pi x / 4)
#   3. x^2 + x - 7 + 3 sin(pi x)
#
# Run with the defaults (30 generations, population 500, tournament size 5):
#   python3 symbolic_regression_gp.py
# or set them yourself, in that order:
#   python3 symbolic_regression_gp.py 50 1000 7
# It asks which problem you want, then shows the dataset, the fitness and
# size curves, and the best expression plotted against the target.

import sys
import operator
import math
import random
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
from deap import algorithms, base, creator, tools, gp

# Default parameters
PopulationSize = 500
TournamentSize = 5
NumGenerations = 30
CrossoverRate = 0.7
MutationRate = 0.3
UseSqError = True  # squared error, otherwise absolute error

TargetFunctions = {
    '1': lambda x: 5 * x**5 + 4 * x**4 + 3 * x**3 + 2 * x**2 + x,
    '2': lambda x: 4 * math.sin(((5 * math.pi) / 4) * x),
    '3': lambda x: x ** 2 + x - 7 + 3 * math.sin(math.pi * x),
}


# Division that returns 1 instead of blowing up on a zero
def protectedDiv(Numerator, Denominator):
    return 1 if Denominator == 0 else Numerator / Denominator


# 65 sample points from -pi to pi and the target value at each one
def create_dataset(TargetFunction):
    InputPoints = np.linspace(-math.pi, math.pi, 65).tolist()
    TargetPoints = [TargetFunction(Input) for Input in InputPoints]
    return InputPoints, TargetPoints


# The building blocks the trees are made of
def create_primitive_set():
    PrimitiveSet = gp.PrimitiveSet("MAIN", 1)
    PrimitiveSet.addPrimitive(operator.add, 2)
    PrimitiveSet.addPrimitive(operator.sub, 2)
    PrimitiveSet.addPrimitive(operator.mul, 2)
    PrimitiveSet.addPrimitive(operator.neg, 1)
    PrimitiveSet.addPrimitive(math.cos, 1)
    PrimitiveSet.addPrimitive(math.sin, 1)
    PrimitiveSet.addPrimitive(protectedDiv, 2)
    PrimitiveSet.addTerminal(1)
    PrimitiveSet.addTerminal(-1)
    PrimitiveSet.addEphemeralConstant("rand101", partial(random.randint, -1, 1))
    PrimitiveSet.renameArguments(ARG0='x')
    return PrimitiveSet


# Mean error between the tree and the target over all the sample points
def EvaluateSymbolicRegression(individual, Toolbox, TargetFunction, InputPoints):
    func = Toolbox.compile(expr=individual)
    if UseSqError:
        error = (abs(func(x) - TargetFunction(x)) ** 2 for x in InputPoints)
    else:
        error = (abs(func(x) - TargetFunction(x)) for x in InputPoints)
    return math.fsum(error) / len(InputPoints),


# Wires up how individuals are made, evaluated, selected, crossed and mutated
def create_toolbox(PrimitiveSet, TargetFunction, InputPoints):
    if not hasattr(creator, "FitnessMin"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)
    Toolbox = base.Toolbox()
    Toolbox.register("expr", gp.genHalfAndHalf, pset=PrimitiveSet, min_=1, max_=2)
    Toolbox.register("individual", tools.initIterate, creator.Individual, Toolbox.expr)
    Toolbox.register("population", tools.initRepeat, list, Toolbox.individual)
    Toolbox.register("compile", gp.compile, pset=PrimitiveSet)
    Toolbox.register("evaluate", EvaluateSymbolicRegression, Toolbox=Toolbox,
                     TargetFunction=TargetFunction, InputPoints=InputPoints)
    Toolbox.register("select", tools.selTournament, tournsize=TournamentSize)
    Toolbox.register("mate", gp.cxOnePoint)
    Toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
    Toolbox.register("mutate", gp.mutUniform, expr=Toolbox.expr_mut, pset=PrimitiveSet)
    # cap the tree height so they do not grow without limit
    Toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=64))
    Toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=64))
    return Toolbox


# Statistics printed every generation: fitness and tree size
def create_mstats_object():
    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("mdn", np.median)
    mstats.register("avg", np.mean)
    mstats.register("std", np.std)
    mstats.register("min", np.min)
    mstats.register("max", np.max)
    return mstats


def plot_dataset(InputPoints, TargetPoints):
    plt.figure(figsize=(15, 4))
    plt.scatter(InputPoints, TargetPoints)
    plt.xlabel('Test points')
    plt.ylabel('Measurements')
    plt.title('Dataset')
    plt.show()


# Median fitness and median tree size per generation, both scaled to 1
def plot_fitness_and_size(Logging):
    x = np.arange(0, NumGenerations + 1)
    s = np.array(Logging.chapters['size'].select("mdn"), dtype=float)
    f = np.array(Logging.chapters['fitness'].select("mdn"), dtype=float)

    fig, ax = plt.subplots()
    ax.plot(x, f / f.max(), 'k--', label='Fitness')
    ax.plot(x, s / s.max(), 'k:', label='Size')
    ax.set_xlabel('Generations')
    ax.set_ylabel('Normalized Fitness/Size')
    ax.set_title('Median')
    ax.legend(shadow=True, fontsize='x-large')
    print('Fitness: [' + str(f.min()) + ', ' + str(f.max()) + ']')
    print('Size: [' + str(s.min()) + ', ' + str(s.max()) + ']')
    print('Evaluations: ' + str(sum(Logging.select("nevals"))))
    plt.show()


# Best evolved expression drawn over the target function
def plot_comparison_Target_Vs_EvolvedSolution(HOF, Toolbox, InputPoints, TargetPoints):
    f = Toolbox.compile(expr=HOF[0])
    y = [f(x) for x in InputPoints]
    plt.plot(InputPoints, y, 'r-', label='Best Solution')
    plt.plot(InputPoints, TargetPoints, 'k-', label='Target function')
    plt.legend(shadow=True, fontsize='x-large')
    plt.show()


def main():
    problem_number = input('Select Problem Number. 1, 2 or 3: ').strip()
    if problem_number not in TargetFunctions:
        print("Pick 1, 2 or 3")
        return
    TargetFunction = TargetFunctions[problem_number]

    InputPoints, TargetPoints = create_dataset(TargetFunction)
    PrimitiveSet = create_primitive_set()
    Toolbox = create_toolbox(PrimitiveSet, TargetFunction, InputPoints)
    MStats = create_mstats_object()
    HOF = tools.HallOfFame(1)  # keeps the single best tree ever seen

    plot_dataset(InputPoints, TargetPoints)

    random.seed()
    Population = Toolbox.population(n=PopulationSize)
    Population, Logging = algorithms.eaSimple(Population, Toolbox, CrossoverRate, MutationRate, NumGenerations,
                                              stats=MStats, halloffame=HOF, verbose=True)

    plot_fitness_and_size(Logging)
    print("Best expression:", HOF[0])
    print("Best fitness:", HOF[0].fitness.values[0])
    plot_comparison_Target_Vs_EvolvedSolution(HOF, Toolbox, InputPoints, TargetPoints)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(f"Using default values for NumGenerations ({NumGenerations}), PopulationSize ({PopulationSize}), and TournamentSize ({TournamentSize}).")
    elif len(sys.argv) == 4:
        try:
            NumGenerations = int(sys.argv[1])
            PopulationSize = int(sys.argv[2])
            TournamentSize = int(sys.argv[3])
        except ValueError:
            print("Error: NumGenerations, PopulationSize, and TournamentSize should be valid integer inputs")
            sys.exit(1)
    else:
        print("Run with no arguments for the defaults, or with three: NumGenerations PopulationSize TournamentSize")
        sys.exit(1)
    main()
