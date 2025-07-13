import pygame
import random

WIDTH = 500
HEIGHT = 500
GRID_WIDTH = 50
GRID_HEIGHT = 50
CELL_SIZE = WIDTH // GRID_WIDTH
MAX_DENSITY = 5
MUTATION_STD = 0.1
BASE_REPRO_PROB = 0.2

def reproduce_vector(vector):
    i = random.randrange(3)
    mutated = vector[:]
    mutated[i] = (mutated[i] + random.gauss(0, MUTATION_STD)) % 256
    return mutated

class Environment:
    def __init__(self, w, h, max_density):
        self.w = w
        self.h = h
        self.max_density = max_density
        self.grid = [[[] for _ in range(w)] for _ in range(h)]
        self.active_cells = set()

    def add(self, x, y, vector):
        self.grid[y][x].append(vector)
        self.active_cells.add((x, y))

    def density(self, x, y):
        return len(self.grid[y][x])

    def compute_fitness(self, vector, x, y):
        return BASE_REPRO_PROB

    def random_adjacent(self, x, y):
        neighbors = []
        for dx in -1,0,1:
            for dy in -1,0,1:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.w and 0 <= ny < self.h:
                    neighbors.append((nx, ny))
        return random.choice(neighbors)

    def step(self):
        offspring = []
        for x,y in list(self.active_cells):
            cell = self.grid[y][x]
            for vector in list(cell):
                if self.density(x, y) < self.max_density:
                    if random.random() < self.compute_fitness(vector, x, y):
                        child = reproduce_vector(vector)
                        nx, ny = self.random_adjacent(x, y)
                        offspring.append((nx, ny, child))
        for x,y,child in offspring:
            cell = self.grid[y][x]
            if len(cell) < self.max_density:
                cell.append(child)
                self.active_cells.add((x, y))
        self.cull()

    def cull(self):
        to_remove = []
        for x,y in list(self.active_cells):
            cell = self.grid[y][x]
            if len(cell) > self.max_density:
                random.shuffle(cell)
                self.grid[y][x] = cell[:self.max_density]
            if not self.grid[y][x]:
                to_remove.append((x, y))
        for coord in to_remove:
            self.active_cells.remove(coord)

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    env = Environment(GRID_WIDTH, GRID_HEIGHT, MAX_DENSITY)
    for _ in range(100):
        x = random.randrange(GRID_WIDTH)
        y = random.randrange(GRID_HEIGHT)
        vector = [random.uniform(0, 255) for _ in range(3)]
        env.add(x, y, vector)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        env.step()
        screen.fill((0,0,0))
        for x, y in env.active_cells:
            for vector in env.grid[y][x]:
                vx, vy, vz = vector
                r = int(vx)
                g = int(vy)
                b = int(vz)
                px = x * CELL_SIZE + CELL_SIZE // 2
                py = y * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(screen, (r, g, b), (px, py), CELL_SIZE // 3)
        pygame.display.flip()
        clock.tick(10)
    pygame.quit()

