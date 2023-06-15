from simulation import Simulation
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as col
from graphs import rectangular_graph

def show_simul(sim: Simulation, axs):
    plot_matrix(axs[0, 0], sim.payoff, vmin=0, vmax=10)
    axs[0,0].set_title("Payoff")
    plot_matrix(axs[0, 1], sim.friendliness, vmin=0, vmax=1)
    axs[0,1].set_title("Friendliness")
    strats = np.array(list(map(lambda x: x.value,sim.strategies)))
    occ = np.array(sim.occupied)
    strats[occ==0] = -1
    colorsList = ['#bcbcbc','#ffd966','#a10d0d']
    plot_matrix(axs[1, 0], strats, False, vmin=-1, vmax=1, cmap=col.ListedColormap(colorsList))
    axs[1,0].set_title("Strategy")
    plot_matrix(axs[1, 1], sim.occupied, False, vmin=0, vmax=1, cmap=plt.cm.Greys)
    axs[1,1].set_title("Occupied")

def plot_matrix(ax: plt.axis, arr, disp_values=True, **kwargs):
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