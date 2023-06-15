import networkx as nx

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