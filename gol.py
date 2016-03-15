from tkinter import *
import numpy

def gameOfLife(rows, cols):

	def redrawAllWrapper(canvas, data):
		canvas.delete(ALL)
		redrawAll(canvas, data)
		canvas.update()

	def mousePressedWrapper(event, canvas, data):
		mousePressed(event, data)
		canvas.update()

	def keyPressedWrapper(event, canvas, data):
		keyPressed(event, data)
		redrawAllWrapper(canvas, data)

	def timerFiredWrapper(canvas, data):
		timerFired(data)
		redrawAllWrapper(canvas, data)
		# pause, then call timerFired again
		canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

	def windowSizeChanged(event, canvas, data):
		data.cellSize = event.height / data.cols
		redrawAllWrapper(canvas, data)


	# Data class
	class Struct(object): pass
	data = Struct()

	# Initialize data
	data.rows = rows
	data.cols = cols
	data.cellSize = 20 # pixels
	data.windowWidth = data.cols * data.cellSize
	data.windowHeight = data.rows * data.cellSize
	data.timerDelay = 50 # milliseconds
	data.neighbors = [(-1, -1), (-1, 0), (-1, 1),
					  ( 0, -1),          ( 0, 1),
					  ( 1, -1), ( 1, 0), ( 1, 1)]
	data.board = initializeBoard(data)
	data.paused = True
	# Game rules
	data.stay = [2,3]
	data.begin = [3]

	# create the root and the canvas
	root = Tk()
	canvas = Canvas(root, width=data.windowWidth, height=data.windowHeight, background = "black")
	canvas.pack()

	# set up events
	root.bind("<Button-1>", lambda event: mousePressedWrapper(event, canvas, data))
	root.bind("<B1-Motion>", lambda event: mousePressedWrapper(event, canvas, data))
	root.bind("<Button-3>", lambda event: mousePressedWrapper(event, canvas, data))
	root.bind("<B3-Motion>", lambda event: mousePressedWrapper(event, canvas, data))
	root.bind("<Key>", lambda event: keyPressedWrapper(event, canvas, data))
	root.bind("<Configure>", lambda event: windowSizeChanged(event, canvas, data))
	timerFiredWrapper(canvas, data)
	root.mainloop()



def initializeBoard(data):
	return set()

def redrawAll(canvas, data):
	drawBoard(canvas, data)

def drawBoard(canvas, data):
	for cell in data.board:
		row, col = cell
		canvas.create_rectangle((data.cellSize*col, data.cellSize*row), (data.cellSize*(col+1), data.cellSize*(row+1)), fill = "white")

def generation(data):
	newBoard = initializeBoard(data)
	for cell in data.board:
		row, col = cell
		# Evaluate alive cell
		count = countNeighbors(data, row, col)
		for n in data.stay:
			if count == n:
				newBoard.add((row,col))
		# Evaluate dead neighbors
		for (dx, dy) in data.neighbors:
			newRow = (row + dy) % data.rows
			newCol = (col + dx) % data.cols
			if (newRow, newCol) not in data.board:
				count = countNeighbors(data, newRow, newCol)
				for n in data.begin:
					if count == n:
						newBoard.add((newRow, newCol))
	data.board = newBoard

def countNeighbors(data, row, col):
	count = 0
	for (dx, dy) in data.neighbors:
		if ((row + dy) % data.rows, (col + dx) % data.cols) in data.board:
			count += 1
	return count

def timerFired(data):
	if not data.paused:
		generation(data)

def mousePressed(event, data):
	# use event.x and event.y
	row = event.y // data.cellSize
	col = event.x // data.cellSize
	data.board.add((row, col))

def keyPressed(event, data):
	# use event.char and event.keysym
	if event.keysym == "space":
		data.paused = not data.paused
	elif event.keysym == "Up":
		data.timerDelay //= 10
	elif event.keysym == "Down":
		data.timerDelay *= 10




gameOfLife(50, 50)