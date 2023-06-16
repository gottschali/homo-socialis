from simulation import Simulation, Strategy
import numpy as np
from graphs import *
import networkx as nx
import matplotlib.pyplot as plt
import itertools as it
import time

class Stats:
    
    def __init__(self, stats):
        self.stats = stats
        
    def __repr__(self) -> str:
        return f"{tuple(self.stats)}"
        
    def update(self, simulation: Simulation):
        for stat in self.stats:
            stat.update(simulation)
            

class Stat:
    name: str
    def __init__(self, name, func):
        self.name = name
        self.values = []
        self.func = func
        
    def __repr__(self):
        return str(self.values[-1])

    def update(self, simulation: Simulation):
        self.values.append(self.func(simulation))

    def avg_from(self, fro=0):
        sample = self.values[fro:]
        return sum(sample) / len(sample)
        
def avg_friendliness(sim: Simulation):
    n = 0
    total_friendly = 0
    for (i, friendliness) in enumerate(sim.friendliness):
        if sim.occupied[i]:
            n += 1
            total_friendly += friendliness
    return total_friendly / n if n else 0

def share_of_cooperation(sim: Simulation):
    n = 0
    cooperators = 0
    for (i, strat) in enumerate(sim.strategies):
        if sim.occupied[i]:
            cooperators += strat == Strategy.cooperate
            n += 1
    return cooperators/ n if n else 0
            
def avg_fitness_using_strat(sim: Simulation, strategy):
    n = 0
    total_pay = 0
    for i, (occupied, strat) in enumerate(zip(sim.occupied, sim.strategies)):
        fitness = sim.fitness(i)
        if occupied and strat == strategy:
            total_pay += fitness
            n += 1
    return total_pay / n if n else 0

    
def experiment():
   # G = nx.planted_partition_graph(50, 3, 1.0, 0.05) 
   G = nx.planted_partition_graph(10, 5, 0.9, 0.1) 
   plot_graph(G)
   sim = Simulation(G, occupation_frac=1.0)
   plot(sim, 1000)
   
def vary_internal_cohesion_separation():
    # probability of edges within clusters
    internal = (1/3, 1/2, 2/3, 0.9, 1.0)
    # probability of edges between clusters
    external = (0.5, 1/3, 0.2, 0.1, 0.05, 0.01)
    l = 10
    k = 5
    generations = 500

    stats = Stats([
        Stat("Share of Cooperation", share_of_cooperation),
        Stat("Average Friendliness", avg_friendliness),
    ])
    results = {
        i: {} for i in internal
    }
    for i, e in it.product(internal, external):
        G = nx.planted_partition_graph(l, k, i, e) 
        sim = Simulation(G, occupation_frac=1.0)
        # get the stats out
        for _ in range(generations):
            stats.update(sim)
            sim.step()
        cooperation = stats.stats[0].avg_from(100)
        friendly = stats.stats[1].avg_from(100)
        results[i][e] = (cooperation, friendly)
        print(f"{i}, {e} -> {(cooperation, friendly)} ")
    return results 

def reproduce():
    sim = Simulation(rectangular_graph(30, 30), local_reproduction=0.95)
    steps = 500
    # generation = int(steps / sim.probability_of_death)
    plot(sim, steps, save=True)
   
def plot(sim: Simulation, steps: int, save=False):
    stats = Stats([
        Stat("Share of Cooperation", share_of_cooperation),
        Stat("Average Friendliness", avg_friendliness),
        Stat("Average Fitness among Cooperators", lambda s : avg_fitness_using_strat(s, Strategy.cooperate)),
        Stat("Average Fitness among Defectors", lambda s : avg_fitness_using_strat(s, Strategy.defect)),
    ])
    generations = list(range(steps))
    for i in generations:
        # print(f"Step {i} of simulation")
        stats.update(sim)
        # print(stats)
        sim.step()

    # Plotting
    fig, axs = plt.subplots(2, 1)
    axs[0].plot(generations, stats.stats[0].values, 'm-', label=stats.stats[0].name)
    axs[0].plot(generations, stats.stats[1].values, 'g-', label=stats.stats[1].name)
    axs[0].set_ylim([0, 1])
    axs[0].set_xlabel('Steps')
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(generations, stats.stats[2].values, 'b-', label=stats.stats[2].name)
    axs[1].plot(generations, stats.stats[3].values, 'r-', label=stats.stats[3].name)
    axs[1].set_xlabel('Steps')
    # axs[1].set_ylabel('Average Payoff among Cooperators and Defectors')
    axs[1].grid(True)
    axs[1].legend()

    fig.tight_layout()
    if save:
        plt.savefig(f"figures/figure{time.ctime()}.png")
    plt.show()

def main():
    reproduce()
    # experiment()
    # vary_internal_cohesion_separation()



if __name__ == "__main__":
    main()