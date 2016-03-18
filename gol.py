from tkinter import *
from tkinter.ttk import *
import RPi.GPIO as GPIO
import random
import pyglet
#import threading

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
		self.speeds = [1,10,100,250,500,1000] #milliseconds
		self.speedIndex = 3
		self.timerDelay = self.speeds[self.speedIndex]
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
		for row in range(self.rows):
			for col in range(self.cols):
				if random.randint(0,8) == 1:
					self.board.add((col,row))


class Music:
# Handles the playing of music

	def __init__(self, gol):
		self.playing = False
		self.playingColumn = 0
		self.gol = gol
		self.notes = {0:"C2", 1:"D2", 2:"F2", 3:"G2", 4:"A2", 5:"C3", 6:"D3", 
					7:"F3", 8:"G3", 9:"A3", 10:"C4", 11:"D4", 12:"F4", 13:"G4", 
					14:"A4", 15:"C5", 16:"D5", 17:"F5", 18:"G5", 19:"A5", 20:"C6", 
					21:"D6", 22:"F6", 23:"G6", 24:"A6"}
		self.leds = LED()
		self.notePins = {0:19,1:20,2:21,3:22,4:23}
		pyglet.options['audio'] = ('directsound', 'openal', 'silent')

	def playColumn(self):
		if self.leds.displaying:
			self.leds.resetLEDs()
		self.pitches = self.getColumnPitches(self.playingColumn)
		for pitch in self.pitches:
			#threading.Thread(target=self.playNote(self.notes[pitch])).start()
			self.playNote(self.notes[pitch])
			noteLetter = pitch % 5
			if self.leds.displaying:
				self.leds.lightLED(self.notePins[noteLetter])
		self.playingColumn = (self.playingColumn + 1) % self.gol.cols

	def getColumnPitches(self, column):
		pitches = set()
		for cell in self.gol.board:
			if cell[1] == column:
				if cell[0] >= 25:
					pitch = self.gol.rows - 1 - cell[0]
				else:
					pitch = cell[0]
				pitches.add(int(pitch))
		return pitches

	def playNote(self, note):
		pyglet.media.load("notes/" + note + ".wav", streaming=False).play()


class LED:

	def __init__(self):
		self.displaying = False

	def pinSetUp(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(18,GPIO.OUT)
		GPIO.setup(19,GPIO.OUT)
		GPIO.setup(20,GPIO.OUT)
		GPIO.setup(21,GPIO.OUT)
		GPIO.setup(22,GPIO.OUT)
		GPIO.setup(23,GPIO.OUT)
		GPIO.setup(24,GPIO.OUT)

	def resetLEDs(self):
		GPIO.output(18,GPIO.HIGH)
		GPIO.output(24,GPIO.HIGH)
		for pin in range(19,24):
			GPIO.output(pin,GPIO.LOW)

	def lightLED(self, pin):
		GPIO.output(pin,GPIO.HIGH)

	def turnOffLEDs(self):
		for pin in range(18,25):
			GPIO.output(pin,GPIO.LOW)


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
		#self.root.maxsize(width=self.windowWidth, height=self.windowHeight)
		self.root.attributes('-fullscreen', True)
		self.canvas = Canvas(self.root, width=self.canvasSize, height=self.canvasSize, background = "black")

		# Load images
		self.playIcon = PhotoImage(file="icons/play.png")
		self.pauseIcon = PhotoImage(file="icons/pause.png")
		self.slowerIcon = PhotoImage(file="icons/slower.png")
		self.fasterIcon = PhotoImage(file="icons/faster.png")
		self.pencilIcon = PhotoImage(file="icons/pencil.png")
		self.eraserIcon = PhotoImage(file="icons/eraser.png")
		self.clearIcon = PhotoImage(file="icons/clear.png")
		self.randomIcon = PhotoImage(file="icons/random.png")
		self.musicOnIcon = PhotoImage(file="icons/music-on.png")
		self.musicOffIcon = PhotoImage(file="icons/music-off.png")
		self.LEDOnIcon = PhotoImage(file="icons/led-on.png")
		self.LEDOffIcon = PhotoImage(file="icons/led-off.png")
		self.sensorOnIcon = PhotoImage(file="icons/sensor-on.png")
		self.sensorOffIcon = PhotoImage(file="icons/sensor-off.png")

		# Buttons/Labels
		self.playPauseButton = Button(self.root, image=self.playIcon, command=self.playPauseButton)
		self.slowerButton = Button(self.root, image=self.slowerIcon, command=self.slowerButton)
		self.fasterButton = Button(self.root, image=self.fasterIcon, command=self.fasterButton)
		self.pencilEraserButton = Button(self.root, image=self.eraserIcon, command=self.pencilEraserButton)
		self.clearButton = Button(self.root, image=self.clearIcon, command=self.clearButton)
		self.randomButton = Button(self.root, image=self.randomIcon, command=self.randomButton)
		self.speedLabel = Label(self.root, text="Speed: " + str(int(1000/self.gol.timerDelay)) + " generations/second")
		self.musicButton = Button(self.root, image=self.musicOffIcon, command=self.musicButton)
		self.LEDButton = Button(self.root, image=self.LEDOffIcon, command=self.LEDButton)
		self.sensorButton = Button(self.root, image=self.sensorOffIcon, command=self.sensorButton)

		# Interface layout
		self.canvas.grid(row=0, column=0, rowspan=4, sticky="W")
		self.playPauseButton.grid(row=0, column=2, sticky="NSEW")
		self.slowerButton.grid(row=0, column=1, sticky="NSEW")
		self.fasterButton.grid(row=0, column=3, sticky="NSEW")
		self.speedLabel.grid(row=1, column=1, columnspan=3, sticky="NS")
		self.pencilEraserButton.grid(row=2, column=1, sticky="NSEW")
		self.clearButton.grid(row=2, column=2, sticky="NSEW")
		self.randomButton.grid(row=2, column=3, sticky="NSEW")
		self.musicButton.grid(row=3, column=1, sticky="NSEW")
		self.LEDButton.grid(row=3, column=2, sticky="NSEW")
		self.sensorButton.grid(row=3, column=3, sticky="NSEW")

		self.root.grid_columnconfigure(0, minsize=480)
		self.root.grid_columnconfigure(1, weight=1)
		self.root.grid_columnconfigure(2, weight=1)
		self.root.grid_columnconfigure(3, weight=1)
		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_rowconfigure(1, weight=0)
		self.root.grid_rowconfigure(2, weight=1)
		self.root.grid_rowconfigure(3, weight=1)

		# Bind events
		# Drawing with left click
		self.canvas.bind("<Button-1>", lambda event: self.mousePressed(event))
		self.canvas.bind("<B1-Motion>", lambda event: self.mousePressed(event))
		self.drawMode = "draw"
		# Keyboard press events
		self.root.bind("<Escape>", lambda event: self.root.attributes("-fullscreen", False))

	def run(self):
		self.timerFired()
		self.root.mainloop()

	def timerFired(self):
		if not self.gol.paused:
			self.gol.generation()
			if self.music.playing:
				self.music.playColumn()
		self.redrawAll()
		self.canvas.after(self.gol.timerDelay, self.timerFired)

	def redrawAll(self):
		self.canvas.delete(ALL)
		if not self.gol.paused and self.music.playing:
			self.canvas.create_rectangle((self.cellSize*self.music.playingColumn, 0), (self.cellSize*(self.music.playingColumn+1), self.cellSize*self.gol.rows), fill = "gray")
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
		self.canvas.update()

	def playPauseButton(self):
		if self.gol.paused:
			self.gol.paused = False
			self.playPauseButton.config(image=self.pauseIcon)
		else:
			self.gol.paused = True
			self.playPauseButton.config(image=self.playIcon)

	def slowerButton(self):
		if self.gol.timerDelay != self.gol.speeds[-1]:
			self.gol.speedIndex += 1
			self.gol.timerDelay = self.gol.speeds[self.gol.speedIndex]
			self.speedLabel.config(text="Speed: " + str(int(1000/self.gol.timerDelay)) + " generations/second")

	def fasterButton(self):
		if self.gol.timerDelay != self.gol.speeds[0]:
			self.gol.speedIndex -= 1
			self.gol.timerDelay = self.gol.speeds[self.gol.speedIndex]
			self.speedLabel.config(text="Speed: " + str(int(1000/self.gol.timerDelay)) + " generations/second")

	def pencilEraserButton(self):
		if self.drawMode == "draw":
			self.drawMode = "erase"
			self.pencilEraserButton.config(image=self.pencilIcon)
		elif self.drawMode == "erase":
			self.drawMode = "draw"
			self.pencilEraserButton.config(image=self.eraserIcon)

	def clearButton(self):
		self.gol.clear()
		self.gol.paused = True
		self.playPauseButton.config(image=self.playIcon)

	def randomButton(self):
		self.gol.random(self.gol.rows)
		self.gol.paused = True
		self.playPauseButton.config(image=self.playIcon)

	def musicButton(self):
		if self.music.playing:
			self.music.playing = False
			self.musicButton.config(image=self.musicOffIcon)
			self.music.leds.displaying = False
			self.LEDButton.config(image=self.LEDOffIcon)
		else:
			self.music.playing = True
			self.musicButton.config(image=self.musicOnIcon)

	def LEDButton(self):
		if self.music.leds.displaying:
			self.music.leds.displaying = False
			self.music.leds.turnOffLEDs()
			self.LEDButton.config(image=self.LEDOffIcon)
		else:
			self.music.leds.displaying = True
			self.music.leds.pinSetUp()
			self.LEDButton.config(image=self.LEDOnIcon)

	def sensorButton(self):
		pass

# RUN
gol = GOL(25, 25)
main = Interface(gol)
main.run()
main.music.leds.turnOffLEDs()