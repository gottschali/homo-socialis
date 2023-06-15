from simulation import Simulation, Strategy
import numpy as np
from graphs import rectangular_graph
import matplotlib.pyplot as plt

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
            
def avg_payoff_using_strat(sim: Simulation, strategy):
    n = 0
    total_pay = 0
    for (occupied, payoff, strat) in zip(sim.occupied, sim.payoff, sim.strategies):
        if occupied and strat == strategy:
            total_pay += payoff
            n += 1
    return total_pay / n if n else 0

    


def main():
    stats = Stats([
        Stat("Share of Cooperation", share_of_cooperation),
        Stat("Average Friendliness", avg_friendliness),
        Stat("Average Payoff among Cooperators", lambda s : avg_payoff_using_strat(s, Strategy.cooperate)),
        Stat("Average Payoff among Defectors", lambda s : avg_payoff_using_strat(s, Strategy.defect)),
    ])
    G = rectangular_graph(20, 20)
    sim = Simulation(G, local_reproduction=1.0)
    steps = 500
    generations = list(range(steps))
    for i in generations:
        print(f"Step {i} of simulation")
        stats.update(sim)
        print(stats)
        sim.step()

    # Plotting
    fig, axs = plt.subplots(2, 1)
    axs[0].plot(generations, stats.stats[0].values, 'm-', label=stats.stats[0].name)
    axs[0].plot(generations, stats.stats[1].values, 'g-', label=stats.stats[1].name)
    axs[0].set_xlabel('Generation')
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(generations, stats.stats[2].values, 'b-', label=stats.stats[2].name)
    axs[1].plot(generations, stats.stats[3].values, 'r-', label=stats.stats[3].name)
    axs[1].set_xlabel('Generation')
    # axs[1].set_ylabel('Average Payoff among Cooperators and Defectors')
    axs[1].grid(True)
    axs[1].legend()

    fig.tight_layout()
    plt.show()



if __name__ == "__main__":
    main()