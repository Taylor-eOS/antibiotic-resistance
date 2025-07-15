import random
from settings import BASE_DEATH_RATE, BASE_REPRO_PROB, CROWDING_PENALTY, MISMATCH_PENALTY, MUTATION_SD, UNLOCK_DISTANCE

class Environment:
    def __init__(self, w, h, max_density, segment_count, west_color, east_color):
        self.w = w
        self.h = h
        self.max_density = max_density
        self.grid = [[[] for _ in range(w)] for _ in range(h)]
        self.active_cells = set()
        self.targets = [
            tuple(
                int(west_color[i] + (east_color[i] - west_color[i]) * band / (segment_count - 1))
                for i in range(3))
            for band in range(segment_count)]
        self.segment = [
            [x * segment_count // w for x in range(w)]
            for _ in range(h)]
        self.gradient_width = max(1, w // (segment_count * 3))

    @staticmethod
    def reproduce_vector(vector):
        i = random.randrange(3)
        mutated = vector[:]
        mutated[i] = min(255, max(0, mutated[i] + random.gauss(0, MUTATION_SD)))
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

    def get_environment_pressure(self, x, y):
        segment = self.segment[y][x]
        segment_start = segment * self.w // len(self.targets)
        segment_end = (segment + 1) * self.w // len(self.targets)
        if segment_end > segment_start:
            position_in_segment = (x - segment_start) / (segment_end - segment_start)
        else:
            position_in_segment = 0.0
        base_pressure = 0.2 + segment * 0.15
        boundary_pressure = 0.4 * position_in_segment
        pressure = base_pressure + boundary_pressure
        return min(2.0, pressure)

    def death_probability(self, vector, x, y):
        segment = self.segment[y][x]
        tr, tg, tb = self.targets[segment]
        r, g, b = vector
        distance = abs(r - tr) + abs(g - tg) + abs(b - tb)
        mismatch = distance / (255 * 3)
        env_pressure = self.get_environment_pressure(x, y)
        mismatch_penalty = mismatch * env_pressure * 0.6
        density = len(self.grid[y][x]) / self.max_density
        density_factor = density**0.5 if density < 1 else 1
        death_rate = BASE_DEATH_RATE + CROWDING_PENALTY * density_factor + mismatch_penalty
        return min(1.0, death_rate)

    def reproduction_probability(self, vector, x, y):
        segment = self.segment[y][x]
        tr, tg, tb = self.targets[segment]
        r, g, b = vector
        distance = abs(r - tr) + abs(g - tg) + abs(b - tb)
        mismatch = distance / (255 * 3)
        base_fitness = 1.0 - mismatch
        env_pressure = self.get_environment_pressure(x, y)
        if env_pressure > 1.0:
            fitness_penalty = mismatch * (env_pressure - 1.0) * 2.0
            base_fitness = max(0.0, base_fitness - fitness_penalty)
        if segment < len(self.targets) - 1:
            next_tr, next_tg, next_tb = self.targets[segment + 1]
            next_distance = abs(r - next_tr) + abs(g - next_tg) + abs(b - next_tb)
            next_mismatch = next_distance / (255 * 3)
            segment_start = segment * self.w // len(self.targets)
            segment_end = (segment + 1) * self.w // len(self.targets)
            if segment_end > segment_start:
                position_in_segment = (x - segment_start) / (segment_end - segment_start)
                if position_in_segment > 0.7 and mismatch < 0.3:
                    next_fitness = 1.0 - next_mismatch
                    base_fitness = max(base_fitness, next_fitness * 0.6)
        return base_fitness * BASE_REPRO_PROB

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
                if random.random() < self.reproduction_probability(vector, x, y):
                    child = self.reproduce_vector(vector)
                    nx, ny = self.random_adjacent(x, y)
                    density = len(self.grid[ny][nx]) / self.max_density
                    placement_prob = max(0, (1 - density) ** 2)
                    if random.random() < placement_prob:
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

