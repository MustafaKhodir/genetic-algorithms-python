#!/usr/bin/env python3
# The Santa Claus riddle: SANTA - CLAUS = XMAS
#
# Nine letters, each stands for a different digit from 0 to 9. An individual
# is a mapping from letter to digit, the fitness is how far the sum is from
# balancing, and the GA stops as soon as it hits zero.
#
# To keep the digits unique the individual is really an ordered list of nine
# different digits (one is left unused), crossover fills in from the other
# parent without repeating, and mutation swaps two letters or brings in the
# unused digit.
#
#   python3 santa_riddle.py

import random
from steady_state_ga import GeneticAlgorithm

letters = ['S', 'A', 'N', 'T', 'C', 'L', 'U', 'X', 'M']


def word_value(individual, word):
    # individual is a list of 9 digits in the order of letters above
    mapping = dict(zip(letters, individual))
    return int(''.join(str(mapping[letter]) for letter in word))


class RiddleGA(GeneticAlgorithm):
    def __init__(self, **kwargs):
        super().__init__(target=letters, minimise=True, **kwargs)

    # Nine different digits chosen from 0 to 9
    def random_individual(self):
        digits = list(range(10))
        random.shuffle(digits)
        return digits[:len(letters)]

    # How far SANTA - CLAUS is from XMAS. Zero means solved.
    def fitness(self, individual):
        santa_value = word_value(individual, 'SANTA')
        claus_value = word_value(individual, 'CLAUS')
        xmas_value = word_value(individual, 'XMAS')
        return abs(santa_value - claus_value - xmas_value)

    # Take the first part of parent1, then fill the rest with parent2's digits
    # in parent2's order, skipping any already used, so nothing repeats
    def crossover(self, parent1, parent2):
        if random.random() >= self.crossover_rate:
            return parent1[:], parent2[:]
        point = random.randint(1, len(letters) - 1)
        return self.fill(parent1[:point], parent2), self.fill(parent2[:point], parent1)

    def fill(self, head, other):
        child = head[:]
        for d in other:
            if len(child) == len(letters):
                break
            if d not in child:
                child.append(d)
        # if the other parent did not have enough new digits, use the spare one
        for d in range(10):
            if len(child) == len(letters):
                break
            if d not in child:
                child.append(d)
        return child

    # Swap two letters, or swap one letter for the digit nobody is using
    def mutate(self, individual):
        mutated = individual[:]
        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                if random.random() < 0.5:
                    j = random.randrange(len(mutated))
                    mutated[i], mutated[j] = mutated[j], mutated[i]
                else:
                    unused = [d for d in range(10) if d not in mutated][0]
                    mutated[i] = unused
        return mutated


def main():
    # This riddle is full of near misses that trap the population, so one run
    # of the GA only solves it some of the time. The fix I settled on is simple:
    # if the best score has not moved for 400 generations, throw the population
    # away and start again, keeping a note of the best mapping seen so far.
    # Each attempt takes a fraction of a second, so even a dozen restarts is
    # only a few seconds.
    santa_genetic_algorithm = RiddleGA(population_size=100, crossover_rate=0.8, mutation_rate=0.1)
    generations = 50000
    restart_after = 400

    best_ever = santa_genetic_algorithm.best()
    best_ever_score = santa_genetic_algorithm.best_score()
    stuck_for = 0
    restarts = 0
    for generation in range(generations):
        santa_genetic_algorithm.evolve()
        if santa_genetic_algorithm.best_score() < best_ever_score:
            best_ever = santa_genetic_algorithm.best()
            best_ever_score = santa_genetic_algorithm.best_score()
            stuck_for = 0
        else:
            stuck_for += 1
        if best_ever_score == 0:
            print(f"Solved at generation {generation} after {restarts} restarts")
            break
        if stuck_for >= restart_after:
            santa_genetic_algorithm.initialize_population()
            stuck_for = 0
            restarts += 1

    mapping = dict(zip(letters, best_ever))
    print("Fittest individual (Santa Claus Riddle):", mapping)
    print("Fitness:", best_ever_score)
    print(f"SANTA = {word_value(best_ever, 'SANTA')}, CLAUS = {word_value(best_ever, 'CLAUS')}, XMAS = {word_value(best_ever, 'XMAS')}")


if __name__ == '__main__':
    main()
