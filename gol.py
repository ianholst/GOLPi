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



def gameOfLife(rows, cols):
	# Initialize game of life instance
	gol = GOL(rows, cols)
	gol.cellSize = 20 # pixels
	gol.windowWidth = gol.cols * gol.cellSize
	gol.windowHeight = gol.rows * gol.cellSize
	gol.timerDelay = 10 # milliseconds

	# Create the root and the canvas
	root = Tk()
	canvas = Canvas(root, width=gol.windowWidth, height=gol.windowHeight, background = "black")
	canvas.pack()

	# Drawing with left click
	root.bind("<Button-1>", lambda event: mousePressed(event, canvas, gol))
	root.bind("<B1-Motion>", lambda event: mousePressed(event, canvas, gol))
	# Erasing with right click
	root.bind("<Button-3>", lambda event: mousePressed(event, canvas, gol))
	root.bind("<B3-Motion>", lambda event: mousePressed(event, canvas, gol))
	# Keyboard press events
	root.bind("<Key>", lambda event: keyPressed(event, canvas, gol))
	# Responsive to window size
	root.bind("<Configure>", lambda event: windowSizeChanged(event, canvas, gol))

	timerFired(canvas, gol)
	root.mainloop()


def redrawAll(canvas, gol):
	canvas.delete(ALL)
	for cell in gol.board:
		row, col = cell
		canvas.create_rectangle((gol.cellSize*col, gol.cellSize*row), (gol.cellSize*(col+1), gol.cellSize*(row+1)), fill = "white")
	canvas.update()

def timerFired(canvas, gol):
	if not gol.paused:
		gol.generation()
	redrawAll(canvas, gol)
	canvas.after(gol.timerDelay, timerFired, canvas, gol)

def mousePressed(event, canvas, gol):
	row = event.y // gol.cellSize
	col = event.x // gol.cellSize
	gol.board.add((row, col))
	canvas.update()

def keyPressed(event, canvas, gol):
	if event.keysym == "space":
		gol.paused = not gol.paused
	elif event.keysym == "Up":
		gol.timerDelay //= 10
		print(gol.timerDelay)
	elif event.keysym == "Down":
		gol.timerDelay *= 10
		print(gol.timerDelay)
	canvas.update()

def windowSizeChanged(event, canvas, gol):
	gol.cellSize = event.height / gol.cols
	redrawAll(canvas, gol)


gameOfLife(50, 50)