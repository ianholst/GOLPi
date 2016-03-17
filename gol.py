from tkinter import *
from tkinter.ttk import *

class GOL:
# Class that represents the Game of Life object

	def __init__(self, rows, cols):
		# Initialize board
		self.board = set()
		# Board dimensions
		self.rows = rows
		self.cols = cols
		# Game rules
		self.stay = [2,3]
		self.begin = [3]
		# Begin paused
		self.paused = True
		self.timerDelay = 10 #milliseconds
		self.neighbors = [(-1,-1), (-1, 0), (-1, 1),
						  ( 0,-1),          ( 0, 1),
						  ( 1,-1), ( 1, 0), ( 1, 1)]

	def generation(self):
		# Temporary new empty board
		newBoard = set()
		# Loop through live cells in the board
		for cell in self.board:
			row, col = cell
			count = self.countNeighbors(row, col)
			# Cell continues to live based on "stay" rules
			for n in self.stay:
				if count == n:
					newBoard.add((row,col))
			# Evaluate dead neighbors
			for (dx, dy) in self.neighbors:
				# Wrap around horizontally and vertically
				newRow = (row + dy) % self.rows
				newCol = (col + dx) % self.cols
				# If the cell is dead
				if (newRow, newCol) not in self.board:
					count = self.countNeighbors(newRow, newCol)
					# Cell comes to life based on "begin" rules
					for n in self.begin:
						if count == n:
							newBoard.add((newRow, newCol))
		self.board = newBoard

	def countNeighbors(self, row, col):
		count = 0
		for (dx, dy) in self.neighbors:
			if ((row + dy) % self.rows, (col + dx) % self.cols) in self.board:
				count += 1
		return count

class Interface:
# Class that represents the interface and all its elements. Automatically initializes GOL class.

	def __init__(self, gol):
		# Initialize game of life instance
		self.gol = gol
		self.cellSize = 20 #pixels
		self.windowWidth = self.gol.cols * self.cellSize
		self.windowHeight = self.gol.rows * self.cellSize

		# Interface elements
		self.root = Tk()
		self.canvas = Canvas(self.root, width=self.windowWidth, height=self.windowHeight, background = "black")

		# Interface layout
		self.canvas.pack()

		# Bind events
		# Drawing with left click
		self.root.bind("<Button-1>", lambda event: self.mousePressed(event))
		self.root.bind("<B1-Motion>", lambda event: self.mousePressed(event))
		# Keyboard press events
		self.root.bind("<Key>", lambda event: self.keyPressed(event))
		# Responsive to window size
		self.root.bind("<Configure>", lambda event: self.windowSizeChanged(event))

		self.drawMode = "draw"

	def run(self):
		self.timerFired()
		self.root.mainloop()

	def timerFired(self):
		if not self.gol.paused:
			self.gol.generation()
		self.redrawAll()
		self.canvas.after(self.gol.timerDelay, self.timerFired)

	def redrawAll(self):
		self.canvas.delete(ALL)
		for cell in self.gol.board:
			row, col = cell
			self.canvas.create_rectangle((self.cellSize*col, self.cellSize*row), (self.cellSize*(col+1), self.cellSize*(row+1)), fill = "white")
		self.canvas.update()

	def mousePressed(self, event):
		row = event.y // self.cellSize
		col = event.x // self.cellSize
		if self.drawMode == "draw":
			self.gol.board.add((row, col))
		elif self.drawMode == "erase":
			self.gol.board.discard((row, col))
		self.canvas.update()

	def keyPressed(self, event):
		if event.keysym == "space":
			self.gol.paused = not self.gol.paused
		elif event.keysym == "Up":
			self.gol.timerDelay //= 10
		elif event.keysym == "Down":
			self.gol.timerDelay *= 10
		elif event.keysym == "e":
			self.drawMode = "erase"
		self.canvas.update()

	def windowSizeChanged(self, event):
		self.cellSize = event.height / self.gol.cols
		self.redrawAll()


# RUN
gol = GOL(20, 20)
main = Interface(gol)
main.run()