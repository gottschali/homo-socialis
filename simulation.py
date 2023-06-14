from enum import Enum
import random
import networkx as nx
import typing

Probability = float # in interval [0, 1]

class Strategy(Enum):
    cooperate = 0
    defect = 1

# TODO
# - Empty sites
#   The parameter occupation_frac specifies how many sites are occupied
#   We use a boolean array track this.
#   With the graph abstraction I think we could eliminate this
#   Now we have to always test whether neighbors are occupied
#   (if they are not they should just be zero? )
#   (but then for the average formula should they be counted in)
# - Understand how reproduction should work

# TODO Need to keep track of stats
# Either
# - use Immutable State object
#   Every simulation step produces a new SimulationState and we can keep a list of them
# - Provide a way to hook in stats functions to record values and maybe plot them afterwards
# - Keep History in some other way

class Simulation:

    def __init__(self, 
                 graph: nx.Graph,
                 occupation_frac: Probability = 0.6,
                 p_death: Probability = 0.05,
                 initial_friendliness=0.0,
                 local_reproduction=0.9,
                 mutation: Probability = 0.2,
                 temptation = 1.1,
                 reward = 1,
                 punishment = 0,
                 sucker = -1,
                 ):
        # Assume node ids are (0, 1, ..., N-1)
        self.graph = graph
        self.N = len(graph.nodes)
        # For player i: index with player i's strategy followed by strategy of an interacting players strategy
        self.payoff_matrix = {
                                Strategy.cooperate: {
                                    Strategy.cooperate: reward,
                                    Strategy.defect: sucker,
                                },
                                Strategy.defect: {
                                    Strategy.cooperate: temptation,
                                    Strategy.defect: punishment,
                                },
                           }
        # Strict Prisoner's Dilemma
        assert temptation > reward
        assert reward > punishment
        assert punishment > sucker

        self.occupation_frac = occupation_frac
        self.probability_of_death = p_death
        self.initial_friendliness = initial_friendliness
        self.local_reproduction = local_reproduction
        self.mutation = mutation

        # TODO Is it possible to store these attributes directly in the nx.Graph ?
        # The current model just uses node ids to index these lists
        # For some graphs from networkx this may not directly work as the nodes could be e.g. tuples
        self.occupied = [int(random.random() < self.occupation_frac) for _ in range(self.N)]
        self.friendliness = [initial_friendliness for _ in range(self.N)]
        self.payoff = [0 for _ in range(self.N)]
        self.strategies = [Strategy.defect for _ in range(self.N)]

    def fitness(self, v):
        """ 
        Sum of all payoffs from interactions with neighbors
        minus 8|S| to ensure non-negative payoffs and avoid
        the reproduction of agents who are exploited by all their neighbors
        """
        sucker = self.payoff_matrix[Strategy.cooperate][Strategy.defect]
        return sum(self.payoff[u] for u in self.graph[v] if self.occupied[u]) - 8 * sucker

    def choose_strategy(self, v):
        # Maximize utility[i] = (1-friendliness[i]) * own_payoff + friendliness[i] *  avg(neighbor_payoff)
        # utility[i | own_strategy=defect], utility[i | own_strategy=cooperate]
        # Myopic Best Response Rule
        # https://en.wikipedia.org/wiki/Best_response
        # Taking other player strats as given
        # All 2^8 strategies or can we use symmetry
        friendliness = self.friendliness[v]
        best_strat = Strategy.defect
        running_utility = -1e10
        # TODO Would be nice to simplify this code
        for strat in Strategy:
            num_neighbors = len(self.graph[v])
            for cooperating_neighbors in range(0, num_neighbors + 1):
                defecting_neighbors = num_neighbors - cooperating_neighbors
                own_payoff = self.payoff_matrix[strat][Strategy.cooperate] * cooperating_neighbors
                neighbor_payoff = self.payoff_matrix[Strategy.cooperate][strat] * cooperating_neighbors
                own_payoff += self.payoff_matrix[strat][Strategy.defect] * defecting_neighbors
                neighbor_payoff += self.payoff_matrix[Strategy.defect][strat] * defecting_neighbors
                avg_neighbor_payoff = neighbor_payoff / num_neighbors
                utility = (1-friendliness) * own_payoff + friendliness *  avg_neighbor_payoff
                if utility >= running_utility:
                    running_utility = utility
                    best_strat = strat
        self.strategies[v] = best_strat
                


    def step(self):
        """ Perform one simulation step """
        # (always for every player)
        for v in self.graph:
            if not self.occupied[v]: continue
            self.choose_strategy(v)

        # Update payoff (sum (for each neighbor based on interaction))
        for v in self.graph:
            if not self.occupied[v]: continue
            self.choose_strategy(v)
            own_strat = self.strategies[v]
            self.payoff[v] = sum(self.payoff_matrix[own_strat][self.strategies[u]] for u in self.graph[v] if self.occupied[u])

        ####################################################
        # TODO Reproduction & Mutation not yet working
        # Update reproductive fitness
        reproductive_fitness = [self.fitness(v) for v in self.graph]

        # Let some individuals die
        dead_sites = []
        for v in self.graph:
            if not self.occupied[v]: continue
            if random.random() < self.probability_of_death:
                self.occupied[v] = 0
                dead_sites.append(v)


        # all individuals that die are replaced by an offspring of surving to ensure constant population size

        # Reproduce
        # Friendliness of offsprings mutate
        empty_sites = [v for v in self.graph if not self.occupied[v]]

        # produce offspring proportionally to payoff in last round (according to fitness I guess)
        # offspring move to closest empty site (probability v local reproduction)
        # with (1-v) move to randomly selected site
        # inherit friendliness except
        # with mu = 0.05 it mutates
        #  0.8 reset to uniform random [0, friendliness_of_parent]
        #  0.2  uniform random [friendliness_of_parent, 1]

        # for site in dead_sites:
            # new_site = random.choice(self.neighbors(self.grid, x, y) if random.random() < self.local_reproduction else empty_sites)
            # friendliness = random.random() * parent_friendliness if random.random() < 0.8 else friendliness_of_parent + (random.random() / (1-friendliness_of_parent))


