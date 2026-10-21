#!/usr/bin/env python3
# Hyperparameter sweep for the ASCII art GA.
#
# Tries every combination of three population sizes, three crossover rates and
# three mutation rates (27 runs), records the best fitness in every generation,
# and plots the curves so you can see which settings climb fastest.
#
#   python3 hyperparameter_analysis.py
#
# Each run goes for 500 generations. The whole sweep took a few minutes on my
# laptop.

import numpy as np
import matplotlib.pyplot as plt
from steady_state_ga import GeneticAlgorithm, target_ascii_art

# The ranges I explored
population_sizes = [50, 100, 200]
crossover_rates = [0.6, 0.8, 1.0]
mutation_rates = [0.05, 0.1, 0.2]
generations = 500


def run(pop_size, crossover_rate, mutation_rate):
    # Returns the best fitness after every generation for one setting
    GA = GeneticAlgorithm(target_ascii_art, population_size=pop_size,
                          crossover_rate=crossover_rate, mutation_rate=mutation_rate)
    fitness_over_generations = []
    for generation in range(generations):
        GA.evolve()
        fitness_over_generations.append(GA.best_score())
    return fitness_over_generations


def main():
    # fitnesses[(pop, cx, mut)] is the list of best fitness per generation
    fitnesses = {}
    for pop_size in population_sizes:
        for crossover_rate in crossover_rates:
            for mutation_rate in mutation_rates:
                print(f"pop {pop_size}, crossover {crossover_rate}, mutation {mutation_rate}")
                fitnesses[(pop_size, crossover_rate, mutation_rate)] = run(pop_size, crossover_rate, mutation_rate)

    # One subplot per population size and crossover rate, one line per mutation rate
    fig, axes = plt.subplots(len(population_sizes), len(crossover_rates), figsize=(15, 10), sharex=True, sharey=True)
    for i, pop_size in enumerate(population_sizes):
        for j, crossover_rate in enumerate(crossover_rates):
            ax = axes[i, j]
            for mutation_rate in mutation_rates:
                ax.plot(range(generations), fitnesses[(pop_size, crossover_rate, mutation_rate)],
                        label=f"Mutation Rate: {mutation_rate}")
            ax.set_title(f"Population Size: {pop_size}, Crossover Rate: {crossover_rate}")
            ax.set_xlabel("Generation")
            ax.set_ylabel("Fitness")
            ax.legend()
    plt.tight_layout()
    plt.show()

    # Mean best fitness across the run for every combination, and the final
    # fitness, so the winner can be read off without the plot
    print("\nmean fitness over the run, and final fitness:")
    for key, curve in fitnesses.items():
        print(f"  pop {key[0]:>3}, crossover {key[1]}, mutation {key[2]:<4}  mean {np.mean(curve):6.1f}  final {curve[-1]}")

    # Sensitivity to the mutation rate: final fitness against mutation rate,
    # one small plot per population size and crossover rate
    fig, axes = plt.subplots(len(population_sizes), len(crossover_rates), figsize=(10, 6), sharex=True)
    for i, pop_size in enumerate(population_sizes):
        for j, crossover_rate in enumerate(crossover_rates):
            ax = axes[i, j]
            finals = [fitnesses[(pop_size, crossover_rate, m)][-1] for m in mutation_rates]
            ax.plot(mutation_rates, finals, marker='o')
            ax.set_title(f"Population Size: {pop_size}, Crossover Rate: {crossover_rate}")
            ax.set_xlabel("Mutation Rate")
            ax.set_ylabel("Fitness")
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
