from tkinter import *
from tkinter.ttk import *
import random
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)

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

	def clear(self):
		self.board = set()

	def random(self, n):
		self.clear()
		for n in range(n):
			x = random.randint(0,self.cols)
			y = random.randint(0,self.rows)
			self.board.add((x,y))


class Music:
# Handles the playing of music

	def __init__(self, gol):
		self.playingColumn = 0
		self.gol = gol
		self.pins={0:19,1:20,2:21,3:22,4:23}
	def getColumnPitches(self, column):
		pitches = set()
		for cell in self.gol.board:
			if cell[1] == column:
				pitch = self.gol.rows - 1 - cell[0]
				pitches.add(pitch)
		return pitches

	def playColumn(self):
		self.pitches = self.getColumnPitches(self.playingColumn)
		for pitch in self.pitches:
			self.playPitch(pitch)
			note = pitch % 5
			self.lightLED(note)
		self.playingColumn = (self.playingColumn + 1) % self.gol.cols
		# GPIO cleanup

	def playPitch(self, pitch):
		# Play with audio library

	def lightLED(self, note):
		GPIO.cleanup()
		GPIO.output(18,GPIO.HIGH)
		GPIO.output(24,GPIO.HIGH)
		GPIO.output(self.pins[note],GPIO.HIGH)

class Interface:
# Class that represents the interface and all its elements. Automatically initializes GOL class.

	def __init__(self, gol):
		# Initialize game of life instance
		self.gol = gol
		self.windowWidth = 800
		self.windowHeight = 480
		self.canvasSize = self.windowHeight
		self.cellSize = self.windowHeight / self.gol.rows

		# Initialize music
		self.music = Music(self.gol)

		# Interface elements
		self.root = Tk()
		self.root.title("GOL")
		self.root.minsize(width=self.windowWidth, height=self.windowHeight)
		self.root.maxsize(width=self.windowWidth, height=self.windowHeight)

		#self.root.attributes('-fullscreen', True)
		self.canvas = Canvas(self.root, width=self.canvasSize, height=self.canvasSize, background = "black")
		# Buttons
		self.playPauseButton = Button(self.root, text="Play/Pause", command=self.playPauseButton)
		self.slowerButton = Button(self.root, text="Slower", command=self.slowerButton)
		self.fasterButton = Button(self.root, text="Faster", command=self.fasterButton)
		self.pencilEraserButton = Button(self.root, text="Pencil/Eraser", command=self.pencilEraserButton)
		self.clearButton = Button(self.root, text="Clear", command=self.clearButton)
		self.randomButton = Button(self.root, text="Random", command=self.randomButton)

		# Interface layout
		padding = 5
		self.canvas.grid(row=0, column=0, rowspan=2)
		self.playPauseButton.grid(row=0, column=2, sticky="NSEW")
		self.slowerButton.grid(row=0, column=1, sticky="NSEW")
		self.fasterButton.grid(row=0, column=3, sticky="NSEW")
		self.pencilEraserButton.grid(row=1, column=1, sticky="NSEW")
		self.clearButton.grid(row=1, column=2, sticky="NSEW")
		self.randomButton.grid(row=1, column=3, sticky="NSEW")

		self.root.grid_columnconfigure(0, minsize=480)
		self.root.grid_columnconfigure(1, weight=1, pad=5)
		self.root.grid_columnconfigure(2, weight=1, pad=5)
		self.root.grid_columnconfigure(3, weight=1, pad=5)
		#self.root.grid_rowconfigure(0, weight=1)
		#self.root.grid_rowconfigure(1, weight=1)
		#self.root.grid_rowconfigure(2, weight=1)
		#self.root.grid_rowconfigure(3, weight=0)

		# Bind events
		# Drawing with left click
		self.canvas.bind("<Button-1>", lambda event: self.mousePressed(event))
		self.canvas.bind("<B1-Motion>", lambda event: self.mousePressed(event))
		# Keyboard press events
		self.root.bind("<Key>", lambda event: self.keyPressed(event))
		self.root.bind("<Escape>", lambda event: self.root.attributes("-fullscreen", False))
		
		self.drawMode = "draw"

	def run(self):
		self.timerFired()
		self.root.mainloop()

	def timerFired(self):
		if not self.gol.paused:
			self.gol.generation()
			self.music.playColumn()
		self.redrawAll()
		self.canvas.after(self.gol.timerDelay, self.timerFired)

	def redrawAll(self):
		self.canvas.delete(ALL)
		for cell in self.gol.board:
			row, col = cell
			self.canvas.create_rectangle((self.cellSize*col, self.cellSize*row), (self.cellSize*(col+1), self.cellSize*(row+1)), fill = "white")
		self.canvas.update()

	def mousePressed(self, event):
		if event.x < self.canvasSize:
			row = event.y // self.cellSize
			col = event.x // self.cellSize
			if self.drawMode == "draw":
				self.gol.board.add((row, col))
			elif self.drawMode == "erase":
				self.gol.board.discard((row, col))
			self.redrawAll()

	def keyPressed(self, event):
		if event.keysym == "space":
			self.playPauseButton()
		elif event.keysym == "Up":
			self.fasterButton()
		elif event.keysym == "Down":
			self.slowerButton()
		elif event.keysym == "c":
			self.clearButton()
		elif event.keysym == "r":
			self.randomButton()
		self.canvas.update()

	def playPauseButton(self):
		self.gol.paused = not self.gol.paused

	def slowerButton(self):
		if self.gol.timerDelay == 0:
			self.gol.timerDelay = 1
		elif self.gol.timerDelay < 1000:
			self.gol.timerDelay *= 10
		print(self.gol.timerDelay)

	def fasterButton(self):
		self.gol.timerDelay //= 10
		print(self.gol.timerDelay)

	def pencilEraserButton(self):
		if self.drawMode == "draw":	self.drawMode = "erase"
		elif self.drawMode == "erase": self.drawMode = "draw"

	def clearButton(self):
		self.gol.clear()
		self.gol.paused = True

	def randomButton(self):
		self.gol.random(self.gol.rows)
		self.gol.paused = True

# RUN
gol = GOL(50, 50)
main = Interface(gol)
main.run()