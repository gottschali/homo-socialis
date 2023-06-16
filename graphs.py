import matplotlib.pyplot as plt
import networkx as nx

from graphs import nx

def rectangular_graph(n, m) -> nx.Graph:
    """
    Creates a m x n graph where every node is connected to its 8 nearest neighbors.
    Periodic bounary condition (wrap around -> torus)
    """
    G = nx.Graph()
    for y in range(m):
        for x in range(n):
            u = y * n + x
            for i in (-1,0,1):
                for j in (-1,0,1):
                    # Sorry for the deep nesting :)
                    if (i == 0 and j == 0): continue
                    v = ((y+j)%m) * n + ((x+i) % n)
                    G.add_edge(u, v)
    return G

def four_neighbours_graph(n, m) -> nx.Graph:
    """
    Creates a m x n graph where every node is connected to its 4 nearest neighbors.
    Periodic bounary condition (wrap around -> torus)
    """
    G = nx.Graph()
    for y in range(m):
        for x in range(n):
            G.add_edge( y * n + x, ((y - 1) % m) * n + ((x + 0) % n))
            G.add_edge( y * n + x, ((y - 0) % m) * n + ((x + 1) % n))
            G.add_edge( y * n + x, ((y + 0) % m) * n + ((x - 1) % n))
            G.add_edge( y * n + x, ((y + 1) % m) * n + ((x + 0) % n))
    return G


def plot_graph(G: nx.Graph):
    nx.draw(G)
    plt.show()