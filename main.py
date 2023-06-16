from simulation import Simulation
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as col
import networkx as nx
from graphs import *

def show_simul(sim: Simulation, axs):
    plot_matrix(axs[0, 0], sim.payoff, vmin=0, vmax=10)
    axs[0,0].set_title("Payoff", y = 1.15)
    plot_matrix(axs[0, 1], sim.friendliness, vmin=0, vmax=1)
    axs[0,1].set_title("Friendliness", y =1.15)
    strats = np.array(list(map(lambda x: x.value,sim.strategies)))
    occ = np.array(sim.occupied)
    strats[occ==0] = -1
    colorsList = ['#bcbcbc','#a10d0d', '#ffd966']
    plot_matrix(axs[1, 0], strats, vmin=-1, vmax=1, cmap=col.ListedColormap(colorsList))
    axs[1,0].set_title("Strategy", y = 1.15)
    plot_matrix(axs[1, 1], sim.occupied, vmin=0, vmax=1, cmap=plt.cm.Greys)
    axs[1,1].set_title("Occupied", y = 1.15)

def plot_matrix(ax: plt.axis, arr, disp_values=False, **kwargs):
    # Only works for rectangular grid
    # For general graphs we need different visualisation
    matrix = np.array(arr)
    n = int(len(arr)**0.5)
    matrix.resize(n, n)
    ax.clear()
    ax.matshow(matrix, **kwargs)
    if disp_values:
        for i in range(n):
            for j in range(n):
                c = np.format_float_positional(matrix[j,i], precision=1)
                ax.text(i, j, c, va='center', ha='center')


def main():
    G = rectangular_graph(30, 30)
    sim = Simulation(G)
    steps = 1000
    figs, axs = plt.subplots(2, 2)
    plt.subplots_adjust(hspace=0.4)
    show_simul(sim, axs)
    for i in range(steps):
        figs.suptitle("Frame " + str(i))
        sim.step()
        show_simul(sim, axs)
        plt.pause(0.1)
    plt.show()


if __name__ == "__main__":
    main()