#!/usr/bin/env python3
# Minimising two standard test functions with the steady state GA.
#
# Sphere:     f(x) = sum of x_i squared, minimum 0 at all zeros
# Rosenbrock: f(x) = sum of 100 (x_i+1 - x_i^2)^2 + (1 - x_i)^2, minimum 0 at all ones
#
# The individuals are binary strings, so each x_i is 0 or 1. That keeps the
# search space small and the GA finds the exact minimum for both.
#
#   python3 fitness_functions.py

import matplotlib.pyplot as plt
from steady_state_ga import GeneticAlgorithm


def sphere_fitness(individual):
    return sum(x ** 2 for x in individual)


def rosenbrock_fitness(individual):
    sum_value = 0
    for i in range(len(individual) - 1):
        sum_value += 100 * (individual[i + 1] - individual[i] ** 2) ** 2 + (1 - individual[i]) ** 2
    return sum_value


class FunctionGA(GeneticAlgorithm):
    # Same GA, but the fitness is the function value and lower is better.
    # target here is just the number of dimensions.
    def __init__(self, objective, num_dimensions, **kwargs):
        self.objective = objective
        super().__init__(target=[0] * num_dimensions, minimise=True, **kwargs)

    def fitness(self, individual):
        return self.objective(individual)


def plot_fitness_convergence(fitness_values, title):
    plt.plot(range(len(fitness_values)), fitness_values)
    plt.title(title)
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.show()


def optimise(name, objective, num_dimensions, generations=1000):
    GA = FunctionGA(objective, num_dimensions, population_size=100, crossover_rate=0.8, mutation_rate=0.1)
    fitness_values = []
    for generation in range(generations):
        GA.evolve()
        fitness_values.append(GA.best_score())

    print(f"Fittest individual ({name} Function): {GA.best()}")
    print(f"Fitness: {GA.best_score()}")
    plot_fitness_convergence(fitness_values, f'{name} Function Fitness Convergence')


def main():
    num_dimensions_sphere = 10
    num_dimensions_rosenbrock = 5
    optimise('Sphere', sphere_fitness, num_dimensions_sphere)
    optimise('Rosenbrock', rosenbrock_fitness, num_dimensions_rosenbrock)


if __name__ == '__main__':
    main()
