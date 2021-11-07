import random


class Board:
	def __init__(self):
		self.board = [[] for _ in range(3)]
		blocks = ['B', 'D', 'A', 'C']
		for b in blocks:
			self.board[0].append(Block(self, b))

	def move(self, block: 'Block', x):
		for column in self.board:
			if len(column) and column[-1] == block:
				block = column.pop()
		self.board[x].append(block)

	def push(self, block: 'Block'):
		block.pushing = True

	def find_under(self, block: 'Block') -> 'Block':
		for column in self.board:
			block_under = None
			for o_block in column:
				if o_block == block:
					return block_under
				block_under = o_block

	def can_move(self, block: 'Block'):
		for column in self.board:
			if len(column) > 0 and column[-1] == block:
				return True
		return False

	def column(self, block: 'Block'):
		for i, column in enumerate(self.board):
			if len(column) > 0 and column[-1] == block:
				return i


class Block:
	def __init__(self, board: Board, name: chr) -> None:
		self.board = board
		self.name = name
		self.satisfied = False
		self.pushing = False
		self.free = False

	def action(self):
		if not self.satisfied:
			if self.free:
				x = random.choice(list({0, 1, 2} - {self.board.column(self)}))
				self.board.move(self, x)
				self.pushing = False
				print(f'I move to {x}')
			else:
				self.board.push(self)
				print(f'I push')
		print(f'I satisfied')

	def perceive(self):
		goal_over = {
			'A': 'B',
			'B': 'C',
			'C': 'D',
			'D': None
		}
		under = self.board.find_under(self)

		if not (under == goal_over[self.name]):
			self.satisfied = False
		elif under is None or (not under.pushing):
			self.satisfied = True
		else:
			self.satisfied = False

		self.free = self.board.can_move(self)

	def __eq__(self, name: 'str') -> bool:
		return self.name == name

	def __repr__(self):
		return f'{self.name}({"S" if self.satisfied else "NS"}, {"F" if self.free else "NF"}, {"P" if self.pushing else "NP"})'


def main():
	board = Board()
	all_satisfied = False
	i = 0
	while not all_satisfied:
		all_satisfied = True
		i += 1
		for column in board.board:
			for block in column:
				print(block)
				block.perceive()
				block.action()
				all_satisfied = all_satisfied and block.satisfied
				print(board.board)
	print(i)


if __name__ == '__main__':
	main()
