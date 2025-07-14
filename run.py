import pygame
import random
from environment import Environment
from settings import SIDE, WIDTH, HEIGHT, GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, MAX_DENSITY, SPEED

def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    return screen, clock, font

def setup_environment():
    env = Environment(GRID_WIDTH, GRID_HEIGHT, MAX_DENSITY)
    for _ in range(100):
        x = random.randrange(GRID_WIDTH)
        y = random.randrange(GRID_HEIGHT)
        vector = [random.uniform(0, 255) for _ in range(3)]
        env.add(x, y, vector)
    return env

def handle_events(paused):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, paused
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused
    return True, paused

def pick_vectors(env):
    mx, my = pygame.mouse.get_pos()
    if mx < GRID_WIDTH * CELL_SIZE:
        x = mx // CELL_SIZE
        y = my // CELL_SIZE
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return env.grid[y][x][:MAX_DENSITY]
    return []

def render_grid(screen, env):
    for x, y in env.active_cells:
        cx = x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2
        for vector in env.grid[y][x]:
            color = (int(vector[0]), int(vector[1]), int(vector[2]))
            pygame.draw.circle(screen, color, (cx, cy), CELL_SIZE // 3)

def render_panel(screen, selected_vectors, font):
    panel_x = GRID_WIDTH * CELL_SIZE
    pygame.draw.rect(screen, (0, 0, 0), (panel_x, 0, SIDE, HEIGHT))
    for i, vector in enumerate(selected_vectors):
        color = (int(vector[0]), int(vector[1]), int(vector[2]))
        y_pos = 10 + i * 30
        pygame.draw.rect(screen, color, (panel_x + 10, y_pos, 20, 20))
        txt = font.render(f"{color}", True, (255, 255, 255))
        screen.blit(txt, (panel_x + 40, y_pos))

def run_simulation():
    screen, clock, font = init_pygame()
    env = setup_environment()
    running = True
    paused = False
    while running:
        running, paused = handle_events(paused)
        selected_vectors = pick_vectors(env)
        if not paused:
            env.step()
        screen.fill((0, 0, 0))
        render_grid(screen, env)
        render_panel(screen, selected_vectors, font)
        pygame.display.flip()
        clock.tick(SPEED)

if __name__ == '__main__':
    run_simulation()

