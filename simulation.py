from enum import Enum
import random
import networkx as nx
import typing
import numpy as np

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
                 temptation = 0.51,
                 reward = 0.5,
                 punishment = 0,
                 sucker = -0.05,
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
        return self.payoff[v] - 8 * sucker

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
                avg_neighbor_payoff = neighbor_payoff / num_neighbors if num_neighbors else 0
                utility = (1-friendliness) * own_payoff + friendliness *  avg_neighbor_payoff
                if utility >= running_utility:
                    running_utility = utility
                    best_strat = strat
        self.strategies[v] = best_strat
                


    def step(self):
        """ Perform one simulation step """

        # 
        # STRATEGY
        # 

        # compute strategies for every player
        for v in self.graph:
            if not self.occupied[v]: continue
            self.choose_strategy(v)

        # Update payoff (sum (for each neighbor based on interaction))
        for v in self.graph:
            if not self.occupied[v]: continue
            own_strat = self.strategies[v]
            self.payoff[v] = sum(self.payoff_matrix[own_strat][self.strategies[u]] for u in self.graph[v] if self.occupied[u])

        # 
        # DEATH
        # 

        dead_sites = []
        for v in self.graph:
            if not self.occupied[v]: continue
            if random.random() < self.probability_of_death:
                self.occupied[v] = 0
                dead_sites.append(v)


        # all individuals that die are replaced by an offspring of surving to ensure constant population size

        #
        # REPRODUCTION
        #
        empty_sites = np.array([v for v in self.graph if not self.occupied[v]])

        # choose the sites that will reproduce
        alive = np.nonzero(self.occupied)[0]
        reproduction_probability = np.maximum(0, [self.fitness(v) for v in alive])
        norm = np.sum(reproduction_probability)
        if norm > 0:
            reproduction_probability = reproduction_probability/np.sum(reproduction_probability)
            parents, number_offsprings = np.unique(np.random.choice(alive, len(dead_sites), p=reproduction_probability), return_counts=True)
        else:
            parents, number_offsprings = np.unique(np.random.choice(alive, len(dead_sites)), return_counts=True)    
        offsprings = np.array([], dtype=int)
        for parent, n_offsprings in zip(parents, number_offsprings):
            # compute amount of local offsprings
            n_local_offsprings = np.random.binomial(n_offsprings, self.local_reproduction)
            n_random_offsprings = n_offsprings - n_local_offsprings

            # compute n_local_offsprings closest empty_sites
            locals = nx.shortest_path_length(self.graph, parent)
            locals = dict((k, locals[k]) for k in empty_sites if k in locals)
            locals = sorted(locals.keys(), key=lambda x:locals[x])
            locals = locals[:n_local_offsprings]

            # update empty_sites and friendliness
            empty_sites = np.setdiff1d(empty_sites, locals)
            for x in locals:
                self.friendliness[x] = self.friendliness[parent]

            # compute n_random_offsprings
            randoms = np.random.choice(empty_sites, n_random_offsprings, replace=False)

            # update empty_sites and friendliness
            empty_sites = np.setdiff1d(empty_sites, randoms)
            for x in randoms:
                self.friendliness[x] = self.friendliness[parent]

            offsprings = np.concatenate((offsprings, locals, randoms))

        offsprings = offsprings.astype(int)
        # update occupied
        for x in offsprings:
            self.occupied[x] = 1
        
        # 
        # MUTATION
        # 

        for o in offsprings:
            # check if mutation
            if (random.uniform(0, 1) <= self.mutation):
                if (random.uniform(0, 1) <= 0.8):
                    self.friendliness[o] = random.uniform(0, self.friendliness[o])
                else:
                    self.friendliness[o] = random.uniform(self.friendliness[o], 1)
        # if no mutation the friendliness stays that of the parent


