from enum import Enum
import random

class Strategy(Enum):
    cooperate = 0
    defect = 1

# Idea: Immutable State object
# Idea: Linearize matrices to vectors 
# - can abstract for different structures by defining different neighborhoods
# - just index with player id like in the math formulas
# Instead of matrices keep player objects?
class Simulation:
    def grid(self, value): 
        return [[value for w in range(self.width)] for h in range(self.height)]

    def __init__(self, width=50, height=50, occupation_frac=0.6, probability_of_death = 0.05, initial_friendliness=0.0,
                 local_reroduction=0.9,
                 mutation=0.2,
                 temptation=1.1,
                 reward=1,
                 punishment=0,
                 sucker=-1,
                 ):
        self.width = width
        self.height = height
        # For player i: index with player i's strategy followed by strategy of an interacting players strategy
        self.payoff_matrix = ((reward, punishment),
                              (temptation, sucker))

        self.occupation_frac = occupation_frac
        self.probability_of_death = probability_of_death
        self.initial_friendliness = initial_friendliness

        self.local_reroduction = local_reroduction
        self.mutation = mutation
        # WIDTH x HEIGHT rectangular lattice
        assert temptation > reward
        assert reward > punishment
        assert punishment > sucker

        self.occupied = self.grid(0)
        for row in self.occupied:
            for i in range(len(row)):
                row[i] = int(random.random() < self.occupation_frac)
        self.friendliness = self.grid(initial_friendliness)
        self.strategies = self.grid(Strategy.defect)
        self.payoff = self.grid(0)


    def neighbors(self, grid, x, y):
        """ Returns list of Moore neighborhood with periodic boundary condition
            That are occupied
        """
        return [grid[(y+i)%self.width][(x+j)%self.height]
                for i in (-1,0,1) for j in (-1,0,1) if i !=j and self.occupied[y][x]]


    def fitness(self, i, j):
        """ 
        Sum of all payoffs from interactions with neighbors
        minus 8|S| to ensure non-negative payoffs and avoid
        the reproduction of agents who are exploited by all their neibhors
        """
        sucker = self.payoff_matrix[1][1]
        return sum(self.neighbors(self.payoff, i, j)) - 8 * sucker

    def choose_strategy(self, x, y):
        # Maximize utility[i] = (1-friendliness[i]) * own_payoff + friendliness[i] *  avg(neighbor_payoff)
        # utility[i | own_strategy=defect], utility[i | own_strategy=cooperate]
        # Myopic Best Response Rule
        # https://en.wikipedia.org/wiki/Best_response
        # Taking other player strats as given
        # All 2^8 strategies or can we use symmetry
        friendliness = self.friendliness[y][x]
        best_strat = Strategy.defect
        running_utility = -1e10
        for strat in Strategy:
            num_neighbors = len(self.neighbors(self.occupied, x, y))
            for cooperating_neighbors in range(0, num_neighbors + 1):
                defecting_neighbors = num_neighbors - cooperating_neighbors
                own_payoff = self.payoff_matrix[strat.value][Strategy.cooperate.value] * cooperating_neighbors
                neighbor_payoff = self.payoff_matrix[Strategy.cooperate.value][strat.value] * cooperating_neighbors
                own_payoff += self.payoff_matrix[strat.value][Strategy.defect.value] * defecting_neighbors
                neighbor_payoff += self.payoff_matrix[Strategy.defect.value][strat.value] * defecting_neighbors
                avg_neighbor_payoff = neighbor_payoff / num_neighbors
                utility = (1-friendliness) * own_payoff + friendliness *  avg_neighbor_payoff
                if utility >= running_utility:
                    running_utility = utility
                    best_strat = strat
        self.strategies[y][x] = best_strat
                


    def step(self):
        """ Perform one simulation step """
        # (always for every player)
        for y in range(self.height):
            for x in range(self.width):
                if not self.occupied[y][x]: continue
                self.choose_strategy(x, y)

        # Update payoff (sum (for each neighbor based on interaction))
        # TODO this is not suited for a one liner
        for y in range(self.height):
            for x in range(self.width):
                if not self.occupied[y][x]: continue
                self.choose_strategy(x, y)
                own_strat = self.strategies[y][x].value
                self.payoff[y][x] = sum(self.payoff_matrix[own_strat][ns.value] for ns in self.neighbors(self.strategies, x, y))

        # Update reproductive fitness
        reproductive_fitness = [[self.fitness(i, j) for j in range(self.width)] for i in range(self.height)]
        # Let individuals die

        dead_sites = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.occupied[y][x]: continue
                if random.random() < self.probability_of_death:
                    self.occupied[y][x] = 0
                    dead_sites.append((x, y))


        # all individuals that die are replaced by an offspring of surving to ensure constant population size

        # Reproduce
        # Friendliness of offsprings mutate
        empty_sites = [(x, y) for y in range(self.height) for x in range(self.width) if not self.occupied[y][x]]

        for site in dead_sites:

            new_site = random.choice(self.neighbors(self.grid, x, y) if random.random() < self.local_reroduction else empty_sites)
            friendliness = random.random() * parent_friendliness if random.random() < 0.8 else friendliness_of_parent + (random.random() / (1-friendliness_of_parent))

        # produce offspring proportionally to payoff in last round (according to fitness I guess)
        # offspring move to closest empty site (probability v local reproduction)
        # with (1-v) move to randomly selected site
        # inherit friendliness except
        # with mu = 0.05 it mutates
        #  0.8 reset to uniform random [0, friendliness_of_parent]
        #  0.2  uniform random [friendliness_of_parent, 1]

