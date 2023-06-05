from simulation import Simulation
import numpy as np
import matplotlib.pyplot as plt

def show_simul(sim: Simulation, axs):
    axs[0,0].set_title("Payoff")
    plot_matrix(axs[0, 0], sim.payoff, vmin=0, vmax=10)
    axs[0,1].set_title("Friendliness")
    plot_matrix(axs[0, 1], sim.friendliness, vmin=0, vmax=1)
    strats = [list(map(lambda x: x.value, row)) for row in sim.strategies]
    axs[1,0].set_title("Strategy")
    plot_matrix(axs[1, 0], strats, vmin=0, vmax=1, cmap=plt.cm.YlOrRd)
    axs[1,1].set_title("occupied")
    plot_matrix(axs[1, 1], sim.occupied, vmin=0, vmax=1, cmap=plt.cm.Greys)

def plot_matrix(ax: plt.axis, matrix, **kwargs):
    # intersection_matrix = np.random.randint(0, 10, size=(max_val, max_val))
    matrix = np.array(matrix)
    rows, cols = matrix.shape
    ax.clear()
    ax.matshow(matrix, **kwargs)
    for i in range(rows):
        for j in range(cols):
            c = matrix[j,i]
            ax.text(i, j, str(c), va='center', ha='center')

def main():
    sim = Simulation(width=15, height=15, initial_friendliness=0.8)
    n = 100
    figs, axs = plt.subplots(2, 2)
    show_simul(sim, axs)
    for i in range(n):
        figs.suptitle("Frame " + str(i))
        sim.step()
        show_simul(sim, axs)
        plt.pause(0.1)
    plt.show()


if __name__ == "__main__":
    main()