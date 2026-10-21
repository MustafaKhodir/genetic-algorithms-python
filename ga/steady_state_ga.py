#!/usr/bin/env python3
# My steady state genetic algorithm, plus the ASCII art demo that uses it.
#
# Steady state means every generation makes just two children, which go into
# the population and the two worst individuals drop out. The population stays
# sorted best first the whole time, so population[0] is always the current best.
#
# The other scripts in this folder import GeneticAlgorithm from here and
# override the bits they need (fitness, how an individual is made, mutation).
#
# Run on its own it evolves a 141 bit binary string into a target ASCII picture:
#   python3 steady_state_ga.py

import random


class GeneticAlgorithm:
    # target is the thing we are evolving towards. For the ASCII art it is the
    # list of target bits. Subclasses can pass whatever they like and read it
    # back in their own fitness method.
    def __init__(self, target, population_size=100, crossover_rate=0.8, mutation_rate=0.1, minimise=False):
        self.target = target
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.minimise = minimise  # False means a higher fitness is better
        self.population = []
        self.scores = []          # fitness of each individual, same order as population
        self.initialize_population()

    # One random individual. Default is a binary string as long as the target.
    def random_individual(self):
        return [random.choice([0, 1]) for _ in range(len(self.target))]

    # Fills the population with random individuals and sorts them best first.
    def initialize_population(self):
        self.population = [self.random_individual() for _ in range(self.population_size)]
        self.scores = [self.fitness(ind) for ind in self.population]
        self.sort_population()

    # Default fitness: how many bits match the target. Higher is better.
    def fitness(self, individual):
        return sum(1 for i, j in zip(individual, self.target) if i == j)

    # True when score a is better than score b, depending on the direction
    def better(self, a, b):
        return a < b if self.minimise else a > b

    def sort_population(self):
        order = sorted(range(len(self.population)), key=lambda k: self.scores[k], reverse=not self.minimise)
        self.population = [self.population[k] for k in order]
        self.scores = [self.scores[k] for k in order]

    # Single point crossover. Only happens with probability crossover_rate,
    # otherwise the parents come back as they are.
    def crossover(self, parent1, parent2):
        if random.random() < self.crossover_rate:
            crossover_point = random.randint(1, len(parent1) - 1)
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            return child1, child2
        return parent1[:], parent2[:]

    # Flips each bit with probability mutation_rate
    def mutate(self, individual):
        mutated_individual = individual[:]
        for i in range(len(mutated_individual)):
            if random.random() < self.mutation_rate:
                mutated_individual[i] = 1 - mutated_individual[i]
        return mutated_individual

    # Tournament selection: pick three at random and keep the best of them.
    # Tournament works the same whether fitness is being maximised or
    # minimised, which is why I chose it over fitness proportional selection.
    def select_one(self):
        picks = random.sample(range(len(self.population)), 3)
        best = min(picks)  # population is sorted best first, so the lowest index wins
        return self.population[best]

    def select_parents(self):
        return self.select_one(), self.select_one()

    # Drops a new individual into the sorted population, keeping it sorted
    def insert(self, individual, score):
        pos = 0
        while pos < len(self.population) and not self.better(score, self.scores[pos]):
            pos += 1
        self.population.insert(pos, individual)
        self.scores.insert(pos, score)

    # One generation: two parents, two children, the two worst go out.
    # A child that is an exact copy of something already in the population is
    # thrown away, otherwise the population fills up with clones of the best
    # one and stops exploring.
    def evolve(self):
        parent1, parent2 = self.select_parents()
        child1, child2 = self.crossover(parent1, parent2)
        for child in (self.mutate(child1), self.mutate(child2)):
            if child in self.population:
                continue
            self.insert(child, self.fitness(child))
        del self.population[self.population_size:]
        del self.scores[self.population_size:]

    def best(self):
        return self.population[0]

    def best_score(self):
        return self.scores[0]


# Prints a binary individual as rows of the given width
def print_ascii_art(binary_individual, width):
    ascii_text = ''.join(str(bit) for bit in binary_individual)
    for i in range(0, len(ascii_text), width):
        print(ascii_text[i:i + width])


# Target ASCII art, 141 bits printed 21 wide
target_ascii_art = [
    0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0,
    0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0]


def main():
    # Mutation 0.1 per bit flips around 14 bits in every child, which is too
    # many once the string is nearly right, so my first runs levelled off at
    # about 100 of the 141 bits. At 0.01 the GA matches all 141 bits in
    # roughly 2500 generations.
    GA = GeneticAlgorithm(target_ascii_art, population_size=200, crossover_rate=0.8, mutation_rate=0.01)
    generations = 5000

    for generation in range(generations):
        GA.evolve()
        # Print the progress every 100 generations
        if generation % 100 == 0:
            print(f"Generation {generation}, Fitness: {GA.best_score()} / {len(target_ascii_art)}")
            print_ascii_art(GA.best(), width=21)
        if GA.best_score() == len(target_ascii_art):
            print(f"Matched the target at generation {generation}")
            break

    print("Final result:")
    print_ascii_art(GA.best(), width=21)
    print(f"Fitness: {GA.best_score()} / {len(target_ascii_art)}")


if __name__ == '__main__':
    main()
