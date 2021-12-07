import time
from argparse import ArgumentParser
from operator import add, pos, truth
from random import choice, random
from typing import Optional, List, Any, Callable, Tuple, Union

from GUI import BoardGUI

kp: float = 0.1
km: float = 0.3
pas_agent: int = 1
error_rate: float = 0.1
distance_diffusion: int = 2


def manhattan_radius(a, b):
    return max(abs(val1-val2) for val1, val2 in zip(a, b))


class Board:
    def __init__(self, n: int = 50, m: int = 50, n_a: int = 300, n_b: int = 300, n_c=300, n_agents: int = 20):
        self.n = n
        self.m = m
        self.n_a = n_a
        self.n_b = n_b
        self.n_c = n_c
        self.list_agents = {}
        self.board = [[[] for _ in range(m)] for _ in range(n)]

        blocs = self.__create_tiles(
            n * m, (self.n_a, lambda: 'A', ()), (self.n_b, lambda: 'B', ()), (self.n_c, lambda: 'C', ()))

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
        agent = Agent(self)
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

    def get_tile_content(self, position: Tuple[int, int]) -> List[Union['Pheromone', str]]:
        k, l = position
        content = self.board[k][l]
        if 'A' in content and 'B' in content:
            raise Exception('Case contenant A et B en même temps...')
        if 'A' in content and 'C' in content:
            raise Exception('Case contenant A et C en même temps...')
        if 'C' in content and 'B' in content:
            raise Exception('Case contenant B et C en même temps...')
        res = []
        for element in content:
            if isinstance(element, Pheromone):
                res.append(element)
            if 'A' in content:
                res += 'A'
            elif 'B' in content:
                res += 'B'
            elif 'C' in content:
                res += 'C'
            else:
                res += '0'
        return res

    def is_agent_waiting(self, position: Tuple[int, int]) -> str:
        k, l = position
        content = self.board[k][l]
        for elem in content:
            if isinstance(elem, Agent):
                if elem.waiting:
                    return True
        return False

    def move_in_direction(self, agent: 'Agent', direction):
        offset = [i * pas_agent for i in direction]
        i, j = list(map(add, self.list_agents[agent], offset))
        k, l = self.list_agents[agent]
        if 0 <= i < self.n and 0 <= j < self.m:
            self.board[k][l].remove(agent)
            self.list_agents[agent] = (i, j)
            self.board[i][j].append(agent)
            return True
        return False

    def move(self, agent: 'Agent', position: Tuple[int, int]):
        k, l = self.list_agents[agent]
        self.board[k][l].remove(agent)
        self.list_agents[agent] = position
        i, j = position
        self.board[i][j].append(agent)

    def pick_up(self, agent: 'Agent'):
        i, j = self.list_agents[agent]
        self.board[i][j].remove(agent.memory[0])

    def drop(self, agent: 'Agent'):
        i, j = self.list_agents[agent]
        self.board[i][j].append(agent.backpack)

    def emit_pheromone(self, agent: 'Agent'):
        pher_position = []
        (i, j) = self.list_agents[agent]
        for k in range(- distance_diffusion, distance_diffusion+1):
            for l in range(- distance_diffusion, distance_diffusion+1):
                if (k, l) != (0, 0) \
                        and 0 <= i + k < self.n \
                        and 0 <= j + l < self.m:
                    pher_position.append((i + k, j + l))
        return Pheromone(self, agent, pher_position)

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


class Pheromone:
    def __init__(self, board: Board, agent: 'Agent', position: List[Tuple]):
        self.board = board
        self.agent = agent
        self.position = position
        self.strength = 100
        for pos in self.position:
            self.board.board[pos[0]][pos[1]].append(self)

    def destroy(self):
        for pos in self.position:
            self.board.board[pos[0]][pos[1]].remove(self)

    def __str__(self) -> str:
        return 'P'


class Agent:
    def __init__(self, board: Board):
        self.board = board
        self.memory = []
        self.position = None
        self.backpack = None
        self.pheromone = None
        self.waiting = False
        self.linked = None

    def perceive(self):
        self.position = self.board.get_position(self)
        self.memory = self.board.get_tile_content(self.position) + self.memory
        self.memory = self.memory[:25]

    def action(self):

        # detected A or B
        if self.memory[0] == 'A' or self.memory[0] == 'B':
            if self.backpack == None and not self.linked and not self.waiting:
                self.chance_to_pick_up_AB()
                self.random_movement()
            else:
                if not self.waiting:
                    self.random_movement()

        # detected pheromone
        elif isinstance(self.memory[0], Pheromone):
            pheromone = self.memory[0]
            if self.backpack == None and not self.linked and not self.waiting:
                pos_agent_waiting = self.board.get_position(pheromone.agent)
                radius_between = manhattan_radius(
                    self.position, pos_agent_waiting)
                if pheromone.strength - 100 / radius_between >= 25:
                    self.linked = pheromone.agent
                    pheromone.destroy()
                    self.board.move(self, self.board.get_position(self.linked))
                    self.linked.pheromone = None
                else:
                    self.random_movement()
            if self.backpack != None:
                self.random_movement()

        # detected C
        elif self.memory[0] == 'C':
            if self.backpack == None and not self.linked and not self.waiting:
                if not self.board.is_agent_waiting(self.position):
                    self.waiting = True
                    self.pheromone = self.board.emit_pheromone(self)
                else:
                    self.random_movement()

            if self.waiting and self.pheromone:
                self.pheromone.strength -= 1
                if self.pheromone.strength == 0:
                    if random() < 0.5:
                        self.waiting = False
                        self.pheromone.destroy()
                        self.pheromone = None
                        self.random_movement()
                    else:
                        self.pheromone.destroy()
                        self.pheromone = self.board.emit_pheromone(self)

            if self.linked and self.backpack == None:
                self.board.pick_up(self)
                self.backpack = self.memory[0]
                self.random_movement()

            if self.backpack != None and not self.pheromone:
                self.random_movement()

        # detected 0
        else:
            if self.backpack == 'A' or self.backpack == 'B':
                self.chance_to_drop()
                self.random_movement()
            elif self.backpack == 'C':
                self.chance_to_drop()
                if self.backpack == None:
                    self.linked.waiting = False
                    self.linked.random_movement()
                    self.linked = None
                self.random_movement()
                pass
            else:
                if not self.waiting:
                    self.random_movement()

    def compute_f(self, obj):
        return self.memory.count(obj) / len(self.memory)

    def random_movement(self):
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
            flag = self.board.move_in_direction(self, direction)

        if self.linked and self.backpack == 'C':
            self.board.move_in_direction(self.linked, direction)

    def chance_to_drop(self):
        f = self.compute_f(self.memory[0])
        if self.backpack is not None and self.memory[0] == '0':
            if random() < (f / (km + f)) ** 2:
                self.board.drop(self)
                self.backpack = None

    def chance_to_pick_up_AB(self):
        f = self.compute_f(self.memory[0])
        if self.memory[0] == 'A' or self.memory[0] == 'B' and self.backpack is None:
            if random() < (kp / (kp + f)) ** 2:
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
    parser.add_argument('-n', type=int, default=50,
                        help='Number of lines in the board')
    parser.add_argument('-m', type=int, default=50,
                        help='Number of columns in the board')
    parser.add_argument('-nA', type=int, default=800,
                        help='Number of \'A\' blocks in the board')
    parser.add_argument('-nB', type=int, default=800,
                        help='Number of \'B\' blocks in the board')
    parser.add_argument('-nC', type=int, default=100,
                        help='Number of \'C\' blocks in the board')
    parser.add_argument('-nAgents', type=int, default=200,
                        help='Number of agents in the board')
    parser.add_argument('-s', '--step-per-frame', type=int,
                        default=1, help='Number of actions per frame')
    parser.add_argument('-t', '--time-between-frames', type=float,
                        default=0, help='The wait time between each frame')
    args = parser.parse_args()
    print(args)
    b = Board(args.n, args.m, args.nA, args.nB,
              args.nC, args.nAgents)
    gui = BoardGUI(b, args.time_between_frames, args.step_per_frame)
    run(b)


if __name__ == '__main__':
    main()
