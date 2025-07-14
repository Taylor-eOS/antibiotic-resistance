import random
from settings import BASE_REPRO_PROB, BASE_DEATH_RATE, CROWDING_PENALTY, MISMATCH_PENALTY

class Environment:
    def __init__(self, w, h, max_density):
        self.w = w
        self.h = h
        self.max_density = max_density
        self.grid = [[[] for _ in range(w)] for _ in range(h)]
        self.active_cells = set()
        self.targets = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 255), (255, 255, 0)]
        segment_count = len(self.targets)
        self.segment = [[x * segment_count // w for x in range(w)] for _ in range(h)]

    @staticmethod
    def reproduce_vector(vector):
        i = random.randrange(3)
        mutated = vector[:]
        mutated[i] = min(255, max(0, mutated[i] + random.gauss(0, 2)))
        return mutated

    def add(self, x, y, vector):
        self.grid[y][x].append(vector)
        self.active_cells.add((x, y))

    def density(self, x, y):
        return len(self.grid[y][x])

    def random_adjacent(self, x, y):
        neighbors = []
        for dx in -1,0,1:
            for dy in -1,0,1:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.w and 0 <= ny < self.h:
                    neighbors.append((nx, ny))
        return random.choice(neighbors)

    def death_probability(self, vector, x, y):
        r, g, b = vector
        tr, tg, tb = self.targets[self.segment[y][x]]
        distance = abs(r - tr) + abs(g - tg) + abs(b - tb)
        influence = max(0, 1 - distance / 765)
        mismatch = 1 - influence
        density = len(self.grid[y][x]) / self.max_density
        density_factor = density**0.5 if density < 1 else 1
        adjusted_density_penalty = CROWDING_PENALTY * density_factor
        return min(1, BASE_DEATH_RATE + MISMATCH_PENALTY * mismatch + adjusted_density_penalty)

    def mortality(self):
        to_remove = []
        for x, y in list(self.active_cells):
            cell = self.grid[y][x]
            survivors = [v for v in cell if random.random() > self.death_probability(v, x, y)]
            if not survivors and cell:
                survivors = [random.choice(cell)]
            self.grid[y][x] = survivors
            if not survivors:
                to_remove.append((x, y))
        for coord in to_remove:
            self.active_cells.remove(coord)

    def reproduce(self):
        offspring = []
        for x, y in list(self.active_cells):
            for vector in list(self.grid[y][x]):
                nx, ny = self.random_adjacent(x, y)
                density = len(self.grid[ny][nx]) / self.max_density
                prob = max(0, (1 - density)**2)
                if random.random() < prob:
                    child = self.reproduce_vector(vector)
                    offspring.append((nx, ny, child))
        return offspring

    def place_offspring(self, offspring):
        for x, y, child in offspring:
            cell = self.grid[y][x]
            if len(cell) < self.max_density:
                cell.append(child)
                self.active_cells.add((x, y))

    def step(self):
        self.mortality()
        offspring = self.reproduce()
        self.place_offspring(offspring)

