import sys
import pygame

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
WINDOW_HEIGHT = 1000
WINDOW_WIDTH = 1200


class BoardGUI:
    IMGS = {
        'ant': pygame.image.load(r'./Ant.png'),
        'ant_A': pygame.image.load(r'./Ant_A.png'),
        'ant_B': pygame.image.load(r'./Ant_B.png'),
        'double_ant_C': pygame.image.load(r'./double_Ant_C.png'),
        'A': pygame.image.load(r'./A.png'),
        'B': pygame.image.load(r'./B.png'),
        'C': pygame.image.load(r'./C.png'),
        'P': pygame.image.load(r'./P.png')
    }

    def __init__(self, board, sleep_time_per_frame=0.1, step_per_frame=1):
        self._step_frame = step_per_frame
        self._sleep_time = sleep_time_per_frame
        self.board = board
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = False
        size = int(WINDOW_WIDTH // (self.board.n * 1.2)
                   ), int(WINDOW_HEIGHT / (self.board.m * 1.2))
        self.imgs = {}
        for obj, name in zip(('*', '*A', '*B', '*C', 'A', 'B', 'C', 'P'), ('ant', 'ant_A', 'ant_B', 'double_ant_C', 'A', 'B', 'C', 'P')):
            self.imgs[obj] = pygame.transform.scale(BoardGUI.IMGS[name], size)
        pygame.init()

    @property
    def step_frame(self) -> int:
        return self._step_frame

    @step_frame.setter
    def step_frame(self, new: int):
        self._step_frame = max(1, int(new))

    @property
    def sleep_time(self) -> float:
        return self._sleep_time

    @sleep_time.setter
    def sleep_time(self, new: float):
        self._sleep_time = max(0., new)

    def draw_grid(self):
        x_size, y_size = WINDOW_WIDTH / self.board.n, WINDOW_HEIGHT / self.board.m
        self.screen.fill(WHITE)

        for lin in range(self.board.m):
            for col in range(self.board.n):
                x, y = x_size * col, y_size * lin
                rect = pygame.Rect(x, y, x_size, y_size)
                pygame.draw.rect(self.screen, BLACK, rect, 1)
                for obj in self.board.board[lin][col]:
                    # if obj != 'P':
                    self.screen.blit(
                        self.imgs[str(obj)], (x + x_size * 0.1, y + y_size * 0.1))

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if event.key == pygame.K_LEFT:
                    self.sleep_time += 0.1
                elif event.key == pygame.K_RIGHT:
                    self.sleep_time -= 0.1
                elif event.key == pygame.K_UP:
                    if mods & pygame.KMOD_CTRL:
                        self.step_frame *= 2
                    else:
                        self.step_frame += 1
                elif event.key == pygame.K_DOWN:
                    if mods & pygame.KMOD_CTRL:
                        self.step_frame *= 0.5
                    else:
                        self.step_frame -= 1
                elif event.key == pygame.K_SPACE:
                    self.running = not self.running
                print(f'{self.step_frame=}, {self.sleep_time=}')

        pygame.display.update()
