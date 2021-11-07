import time
from argparse import ArgumentParser
from operator import add
from random import choice, random
from typing import Optional, List, Any, Callable, Tuple

from GUI import BoardGUI

kp: float = 0.1
km: float = 0.3
pas_agent: int = 1
error_rate: float = 0.1


class Board:
    def __init__(self, n: int = 50, m: int = 50, n_a: int = 1200, n_b: int = 1200, n_agents: int = 20, variant=True):
        self.n = n
        self.m = m
        self.n_a = n_a
        self.n_b = n_b
        self.list_agents = {}
        self.board = [[[] for _ in range(m)] for _ in range(n)]
        self.variant = variant

        blocs = self.__create_tiles(
            n * m, (self.n_a, lambda: 'A', ()), (self.n_b, lambda: 'B', ()))
        self.__add_to_board(blocs)
        agents = self.__create_tiles(
            n * m, (n_agents, self.__create_agent, ()))
        self.__add_to_board(agents)

    def __add_to_board(self, tiles):
        for i, line in enumerate(self.board):
            for j, case in enumerate(line):
                x = choice(tiles)
                tiles.remove(x)
                if x is not None:
                    case.append(x)
                    if isinstance(x, Agent):
                        self.list_agents[x] = (i, j)

    def __create_agent(self):
        agent = Agent(self, self.variant)
        self.list_agents[agent] = None
        return agent

    @staticmethod
    def __create_tiles(total_tiles: int, *items: Tuple[int, Callable, Any]) -> List[Optional[Any]]:
        total_items = 0
        tiles_items = []
        for n_item, item, args in items:
            total_items += n_item
            for _ in range(n_item):
                tiles_items.append(item(*args))
        tiles = [None] * (total_tiles - total_items)
        return tiles + tiles_items

    def get_position(self, agent: 'Agent'):
        return self.list_agents[agent]

    def get_tile_content(self, position: Tuple[int, int]) -> str:
        k, l = position
        content = self.board[k][l]
        if 'A' in content and 'B' in content:
            raise Exception('Case contenant A et B en même temps...')
        if 'A' in content:
            return 'A'
        elif 'B' in content:
            return 'B'
        else:
            return '0'

    def move(self, agent: 'Agent', direction):
        offset = [i * pas_agent for i in direction]
        i, j = list(map(add, self.list_agents[agent], offset))
        k, l = self.list_agents[agent]
        if 0 <= i < self.n and 0 <= j < self.m:
            self.board[k][l].remove(agent)
            self.list_agents[agent] = (i, j)
            self.board[i][j].append(agent)
            return True
        return False

    def pick_up(self, agent: 'Agent'):
        i, j = self.list_agents[agent]
        self.board[i][j].remove(agent.memory[0])

    def drop(self, agent: 'Agent'):
        i, j = self.list_agents[agent]
        self.board[i][j].append(agent.backpack)

    def __str__(self):
        res = '_' * (self.n * 3)
        for lin in range(self.m):
            res += '\n|'
            for col in range(self.n):
                case = ''
                for obj in self.board[lin][col]:
                    case += obj.__str__()
                case = f'{case:>2}|'
                res += case
            res += '\n' + '_' * (self.n * 3)
        return res


class Agent:
    def __init__(self, board: Board, variant: bool):
        self.board = board
        self.memory = ''
        self.backpack = None
        self.variant = variant

    def perceive(self):
        position = self.board.get_position(self)
        self.memory = self.board.get_tile_content(position) + self.memory
        self.memory = self.memory[:10]

    def action(self):
        f = self.compute_f() if not self.variant else self.compute_f_with_error()
        if self.memory[0] != '0' and self.backpack is None:
            if random() < (kp / (kp + f)) ** 2:
                self.pick_up()
        if self.backpack is not None and self.memory[0] == '0':
            if random() < (f / (km + f)) ** 2:
                self.drop()

        flag = False
        directions = [
            [0, 1],
            [0, -1],
            [-1, 0],
            [1, 0],
            [-1, 1],
            [1, 1],
            [-1, -1],
            [1, -1]
        ]
        while not flag:
            direction = choice(directions)
            directions.remove(direction)
            flag = self.board.move(self, direction)

    def compute_f(self):
        return self.memory.count(self.memory[0]) / len(self.memory)

    def compute_f_with_error(self):
        return (self.memory.count(self.memory[0]) + self.memory.count('B' if self.memory[0] == 'A' else 'A')) / len(
            self.memory)

    def drop(self):
        self.board.drop(self)
        self.backpack = None

    def pick_up(self):
        self.board.pick_up(self)
        self.backpack = self.memory[0]

    def __str__(self):
        return f'*' + (self.backpack if self.backpack else '')


def main():
    def step(board):
        for agent in board.list_agents:
            agent.perceive()
            agent.action()

    def run(board):
        while True:
            gui.draw_grid()
            gui.update()

            if gui.running:
                time.sleep(gui.sleep_time)
                for i in range(gui.step_frame):
                    step(board)
            else:
                time.sleep(1)

    parser = ArgumentParser('Launch yes SMA project with arguments')
    parser.add_argument('-n', type=int, default=50, help='Number of lines in the board')
    parser.add_argument('-m', type=int, default=50, help='Number of columns in the board')
    parser.add_argument('-nA', type=int, default=200, help='Number of \'A\' blocks in the board')
    parser.add_argument('-nB', type=int, default=200, help='Number of \'B\' blocks in the board')
    parser.add_argument('-nAgents', type=int, default=20, help='Number of agents in the board')
    parser.add_argument('-v', '--variant', action="store_true", help='Use the variant with errors')
    parser.add_argument('-s', '--step-per-frame', type=int, default=1, help='Number of actions per frame')
    parser.add_argument('-t', '--time-between-frames', type=float, default=0, help='The wait time between each frame')
    args = parser.parse_args()
    print(args)
    b = Board(args.n, args.m, args.nA, args.nB, args.nAgents, args.variant)
    gui = BoardGUI(b, args.time_between_frames, args.step_per_frame)
    run(b)


if __name__ == '__main__':
    main()
