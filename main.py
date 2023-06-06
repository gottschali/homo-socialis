from simulation import Simulation
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

def show_simul(sim: Simulation, axs):
    axs[0,0].set_title("Payoff")
    plot_matrix(axs[0, 0], sim.payoff, vmin=0, vmax=10)
    axs[0,1].set_title("Friendliness")
    plot_matrix(axs[0, 1], sim.friendliness, vmin=0, vmax=1)
    strats = list(map(lambda x: x.value,sim.strategies))
    axs[1,0].set_title("Strategy")
    plot_matrix(axs[1, 0], strats, vmin=0, vmax=1, cmap=plt.cm.YlOrRd)
    axs[1,1].set_title("occupied")
    plot_matrix(axs[1, 1], sim.occupied, vmin=0, vmax=1, cmap=plt.cm.Greys)

def plot_matrix(ax: plt.axis, arr, **kwargs):
    # Only works for rectangular grid
    # For general graphs we need different visualisation
    matrix = np.array(arr)
    n = int(len(arr)**0.5)
    matrix.resize(n, n)
    ax.clear()
    ax.matshow(matrix, **kwargs)
    for i in range(n):
        for j in range(n):
            c = matrix[j,i]
            ax.text(i, j, str(c), va='center', ha='center')

def rectangular_graph(m, n,) -> nx.Graph:
    """
    Creates a m x n graph where every node is connected to its 8 nearest neighbors.
    Periodic bounary condition (wrap around -> torus)
    """
    G = nx.Graph()
    for y in range(m):
        for x in range(n):
            for i in (-1,0,1):
                for j in (-1,0,1):
                    # Sorry for the deep nesting :)
                    if i ==j: continue
                    u = y * m + x
                    v = ((y+i)%m) * m + ((x+j) % n)
                    G.add_edge(u, v)
    return G

def main():
    # This graph is connected to 4 nearest neighbors and not the 8 as in the paper!
    # G = nx.grid_2d_graph(m=15, n=15, periodic=True)
    G = rectangular_graph(15, 15)
    sim = Simulation(G, initial_friendliness=0.5)
    steps = 100
    figs, axs = plt.subplots(2, 2)
    show_simul(sim, axs)
    for i in range(steps):
        figs.suptitle("Frame " + str(i))
        sim.step()
        show_simul(sim, axs)
        plt.pause(0.1)
    plt.show()


if __name__ == "__main__":
    main()